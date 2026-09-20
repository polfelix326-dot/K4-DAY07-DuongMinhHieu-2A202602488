"""Compare three strategies and Q5 filtering, with explicitly labelled evidence checks."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from bench import ROOT, ingest, make_chunker
from src import EmbeddingStore, KnowledgeBaseAgent, MockEmbedder


def normalize(text):
    return ' '.join(text.split()).casefold()


def evidence_metrics(query, results):
    gold = query['gold_doc_id']
    needles = [normalize(s) for s in query['evidence_substrings']]
    rank = next((i for i, r in enumerate(results, 1) if r['metadata']['doc_id'] == gold), None)
    # Only credit evidence from the requested source, not coincidental text in another year/document.
    found, coverage_rank = set(), None
    for i, result in enumerate(results, 1):
        if result['metadata']['doc_id'] == gold:
            body = normalize(result['content'])
            found.update(n for n in needles if n in body)
        if len(found) == len(needles) and coverage_rank is None:
            coverage_rank = i
    return {
        'gold_document_rank': rank,
        'document_hit': rank is not None,
        'evidence_hit': coverage_rank is not None,
        'evidence_coverage_rank': coverage_rank,
        'missing_evidence': [n for n in needles if n not in found],
        'retrieval_proxy_score': 2 if coverage_rank == 1 else 1 if coverage_rank else 0,
        'official_score': None,
    }


class SelectedResults:
    """Give the agent exactly the already-filtered retrieval context being evaluated."""
    def __init__(self, results):
        self.results = results

    def search(self, question, top_k=3):
        return self.results[:top_k]


def extractive_preview(prompt):
    """Return retrieved source excerpts, never a gold answer or a generated answer."""
    context = prompt.split('NGỮ CẢNH:\n', 1)[1].rsplit('\n\nCÂU HỎI:', 1)[0]
    return 'BẢN TRÍCH NGỮ CẢNH (không phải câu trả lời tổng hợp của LLM):\n' + context


def evaluate(store, query, filters):
    results = store.search_with_filter(query['question'], top_k=3, metadata_filter=filters)
    metrics = evidence_metrics(query, results)
    preview = KnowledgeBaseAgent(SelectedResults(results), extractive_preview).answer(query['question'])
    return {'filter': filters, 'results': results, **metrics,
            'agent_mode': 'extractive-context-preview', 'agent_answer': preview,
            'agent_correct': None}


def make_embedder(backend):
    if backend == 'mock':
        return MockEmbedder()
    from src import LocalEmbedder
    return LocalEmbedder()  # Fail explicitly if unavailable; never silently switch backend.


def run(backend='mock', size=500, output_dir=ROOT / 'benchmark/cp6'):
    queries_path = ROOT / 'benchmark/usth_queries.json'
    queries = json.loads(queries_path.read_text(encoding='utf-8'))
    if len(queries) != 5:
        raise ValueError('Exactly five queries required')
    embedder = make_embedder(backend)
    cache = {}

    def embed(text):
        key = hashlib.sha256(text.encode('utf-8')).hexdigest()
        if key not in cache:
            vector = embedder(text)
            norm = math.sqrt(sum(x*x for x in vector))
            cache[key] = [x/norm for x in vector] if norm else vector
        return cache[key]

    output_dir.mkdir(parents=True, exist_ok=True)
    summary = {'backend': backend, 'backend_name': embedder._backend_name,
               'chunk_size': size, 'top_k': 3,
               'queries_sha256': hashlib.sha256(queries_path.read_bytes()).hexdigest(),
               'scoring_note': 'retrieval_proxy_score is evidence coverage only, NOT official rubric/LLM correctness.',
               'agent_note': 'No generative LLM configured. Agent emits source context through a labelled extractive llm_fn; correctness ungraded.',
               'strategies': {}}
    for strategy in ('fixed', 'recursive', 'heading'):
        docs, bodies = ingest(ROOT / 'data/hoc-phi-usth', make_chunker(strategy, size))
        for query in queries:
            if not all(normalize(n) in normalize(bodies[query['gold_doc_id']]) for n in query['evidence_substrings']):
                raise ValueError('Gold evidence missing: ' + query['id'])
        store = EmbeddingStore(strategy, embedding_fn=embed)
        store.add_documents(docs)
        evaluations = {q['id']: evaluate(store, q, q['metadata_filter']) for q in queries}
        q5 = next(q for q in queries if q['id'] == 'Q5')
        unfiltered = evaluate(store, q5, {})
        filtered = evaluations['Q5']
        same = [r['id'] for r in filtered['results']] == [r['id'] for r in unfiltered['results']]
        data = {'chunk_count': len(docs), 'avg_length': sum(len(d.content) for d in docs)/len(docs),
                'max_length': max(len(d.content) for d in docs),
                'documents': {name: {'count': sum(d.metadata['doc_id']==name for d in docs)} for name in bodies},
                'evaluations': evaluations,
                'ab_q5': {'without_filter': unfiltered, 'with_filter': filtered,
                          'same_top3': same, 'filter_necessity_proven': False},
                'document_hits': sum(v['document_hit'] for v in evaluations.values()),
                'evidence_hits': sum(v['evidence_hit'] for v in evaluations.values()),
                'retrieval_proxy_total': sum(v['retrieval_proxy_score'] for v in evaluations.values())}
        summary['strategies'][strategy] = data
        lines = [f'CP6 strategy={strategy}; backend={backend}; chunk_size={size}; top_k=3',
                 f'Chunks={data["chunk_count"]}; avg_length={data["avg_length"]:.2f}; max_length={data["max_length"]}',
                 summary['scoring_note'], summary['agent_note']]
        if backend == 'mock':
            lines.append('MOCK MD5: scores do not encode semantic similarity; no semantic winner can be inferred.')
        for q in queries:
            for label, value in [('FILTERED', evaluations[q['id']])] + ([('UNFILTERED A/B', unfiltered)] if q['id']=='Q5' else []):
                lines += ['', f'{q["id"]} {label}: {q["question"]}', 'Gold: '+q['gold_answer'],
                          'Filter: '+json.dumps(value['filter'], ensure_ascii=False),
                          f'doc_hit={value["document_hit"]}; evidence_hit={value["evidence_hit"]}; proxy={value["retrieval_proxy_score"]}/2; official_score=NOT_GRADED']
                for i,r in enumerate(value['results'],1):
                    lines += [f'[{i}] {r["id"]}; score={r["score"]:.6f}; audience={r["metadata"]["audience"]}',
                              'Source: '+r['metadata']['source_url'], r['content']]
                lines += [value['agent_answer']]
        lines += ['',f'Q5 same_top3={same}; necessity of filter NOT proven; generative answer NOT evaluated.']
        text='\n'.join(lines)+'\n'
        (output_dir/f'{strategy}.txt').write_text(text,encoding='utf-8')
        if strategy=='heading':
            (ROOT/'ket_qua_benchmark.txt').write_text(text,encoding='utf-8')
        print(f'{strategy}: chunks={len(docs)}, document_hits={data["document_hits"]}/5, evidence_hits={data["evidence_hits"]}/5, proxy={data["retrieval_proxy_total"]}/10, Q5_same={same}')
    (output_dir/'results.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    return summary


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend',choices=['mock','local'],default='mock')
    parser.add_argument('--chunk-size',type=int,default=500)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'benchmark/cp6')
    args=parser.parse_args()
    run(args.backend,args.chunk_size,args.output_dir)
