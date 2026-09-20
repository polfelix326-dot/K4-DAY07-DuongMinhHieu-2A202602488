"""Validate the corpus's flat, JSON-quoted YAML metadata and source manifest."""
import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

REQUIRED = ('doc_id', 'title', 'source_url', 'retrieved_at', 'document_version', 'audience')


def read_document(path):
    text = path.read_text(encoding='utf-8-sig').replace('\r\n', '\n')
    if not text.startswith('---\n'):
        raise ValueError(f'{path}: missing frontmatter')
    front, body = text[4:].split('\n---\n', 1)
    metadata = {}
    for line in front.splitlines():
        key, value = line.split(':', 1)
        if key in metadata:
            raise ValueError(f'{path}: duplicate key {key}')
        metadata[key] = json.loads(value.strip())
    return metadata, body.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', nargs='?', type=Path, default=Path('data/hoc-phi-usth'))
    args = parser.parse_args()
    docs = sorted(args.directory.glob('*.md'))
    errors, ids, audiences = [], [], Counter()
    with (args.directory / 'sources.csv').open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    for path in docs:
        try:
            meta, body = read_document(path)
            issues = [f'missing {key}' for key in REQUIRED if not meta.get(key)]
            if meta.get('doc_id') != path.stem:
                issues.append('doc_id does not match filename')
            if meta.get('audience') not in {'student', 'faculty', 'staff', 'all'}:
                issues.append('invalid audience')
            if not any(meta.get(k) for k in ('category', 'department', 'language', 'academic_year')):
                issues.append('missing additional filter field')
            if not body:
                issues.append('empty content')
            date.fromisoformat(meta['retrieved_at'])
            url = urlparse(meta['source_url'])
            if url.scheme not in {'https', 'http'} or not url.netloc:
                issues.append('invalid source_url')
            matches = [r for r in rows if r['doc_id'] == meta['doc_id']]
            if len(matches) != 1:
                issues.append('manifest must contain exactly one matching row')
            else:
                row = matches[0]
                for key in REQUIRED[:5]:
                    if row.get(key) != meta[key]:
                        issues.append(f'manifest mismatch: {key}')
                if Path(row['file_path']).resolve() != path.resolve():
                    issues.append('manifest file_path mismatch')
            ids.append(meta['doc_id'])
            audiences[meta['audience']] += 1
            errors.extend(f'{path.name}: {issue}' for issue in issues)
            print(f'{path.name}: {"FAIL" if issues else "OK"}; body_chars={len(body)}')
        except (ValueError, KeyError) as exc:
            errors.append(f'{path.name}: {exc}')
    if not 5 <= len(docs) <= 10:
        errors.append('expected 5-10 documents')
    if len(ids) != len(set(ids)):
        errors.append('duplicate document ids')
    if Counter(r['doc_id'] for r in rows) != Counter(ids):
        errors.append('manifest is not one-to-one')
    if len(audiences) < 2:
        errors.append('expected at least two audiences')
    print(f'files={len(docs)}; csv_rows={len(rows)}; audiences={dict(audiences)}')
    print('\n'.join(errors) if errors else 'PASS: corpus metadata and manifest checks')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
