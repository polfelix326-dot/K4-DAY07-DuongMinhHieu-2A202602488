"""CP5 retrieval benchmark. Default mock embeddings measure plumbing, not meaning."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.check_corpus import read_document
from src import ChunkingStrategyComparator, Document, EmbeddingStore, FixedSizeChunker, MockEmbedder, RecursiveChunker, SentenceChunker
from src.heading_chunking import HeadingChunker

ROOT = Path(__file__).resolve().parent
DEFAULT_STRATEGY = "heading"  # Change only this line for a member's strategy.


def make_chunker(strategy: str, size: int):
    if size <= 0:
        raise ValueError("chunk_size must be positive")
    return {
        "fixed": lambda: FixedSizeChunker(size, min(50, size - 1)),
        "sentence": lambda: SentenceChunker(3),
        "recursive": lambda: RecursiveChunker(chunk_size=size),
        "heading": lambda: HeadingChunker(size),
    }[strategy]()


def ingest(directory: Path, chunker):
    documents, originals = [], {}
    for path in sorted(directory.glob("*.md")):
        metadata, body = read_document(path)
        if metadata.get("doc_id") != path.stem:
            raise ValueError(f"doc_id differs from filename: {path}")
        originals[path.stem] = body
        for index, chunk in enumerate(chunker.chunk(body)):
            documents.append(Document(
                id=f"{path.stem}#{index}", content=chunk,
                metadata={**metadata, "doc_id": path.stem, "chunk_index": index,
                          "source": path.as_posix()},
            ))
    if not documents:
        raise ValueError("No document chunks found")
    return documents, originals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy", choices=["fixed", "sentence", "recursive", "heading"], default=DEFAULT_STRATEGY)
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data/hoc-phi-usth")
    parser.add_argument("--queries", type=Path, default=ROOT / "benchmark/usth_queries.json")
    parser.add_argument("--output", type=Path, default=ROOT / "ket_qua_benchmark.txt")
    parser.add_argument("--baseline-output", type=Path, default=ROOT / "benchmark/baseline_cp5.json")
    args = parser.parse_args()
    queries = json.loads(args.queries.read_text(encoding="utf-8"))
    if len(queries) != 5 or len({q["id"] for q in queries}) != 5:
        raise ValueError("Expected exactly 5 uniquely identified benchmark queries")
    docs, originals = ingest(args.data_dir, make_chunker(args.strategy, args.chunk_size))
    for query in queries:
        body = originals[query["gold_doc_id"]]
        if not all(part in body for part in query["evidence_substrings"]):
            raise ValueError(f"Gold evidence missing: {query['id']}")
    embedder = MockEmbedder()
    store = EmbeddingStore("usth_cp5", embedding_fn=embedder)
    store.add_documents(docs)
    lines = [f"Strategy: {args.strategy}; chunk_size={args.chunk_size}; fixed_overlap=min(50,size-1); sentence_count=3",
             "Backend: MockEmbedder (MD5; no semantic meaning). CP5 only; no LLM answer or quality score.",
             f"Documents: {len(originals)}; stored chunks: {store.get_collection_size()}"]
    for query in queries:
        lines += ["", f"{query['id']}: {query['question']}",
                  f"Filter: {json.dumps(query['metadata_filter'], ensure_ascii=False)}",
                  f"Gold: {query['gold_answer']}",
                  f"Gold source: {query['gold_doc_id']} / {query['gold_section']}"]
        results = store.search_with_filter(query["question"], top_k=3, metadata_filter=query["metadata_filter"])
        for rank, result in enumerate(results, 1):
            lines += [f"[{rank}] score={result['score']:.6f}; doc_id={result['metadata']['doc_id']}; chunk_id={result['id']}; audience={result['metadata']['audience']}",
                      f"source_url={result['metadata']['source_url']}", result["content"]]
        if not results:
            lines.append("No results.")
    lines += ["", "Q5: filter configured; necessity and answer correctness NOT validated. Run A/B in CP6."]
    output = "\n".join(lines) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(output)

    baseline_ids = ["muc-hoc-phi-2026-2027", "thu-hoc-phi-hk2-2025-2026", "phi-gia-han-dao-tao-2025-2026"]
    baseline = {name: ChunkingStrategyComparator().compare(originals[name], args.chunk_size)
                for name in baseline_ids if name in originals}
    args.baseline_output.parent.mkdir(parents=True, exist_ok=True)
    args.baseline_output.write_text(json.dumps({"chunk_size": args.chunk_size, "frontmatter_removed": True,
                                               "documents": baseline}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
