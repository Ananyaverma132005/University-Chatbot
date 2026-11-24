"""Build the static GitHub Pages demo into _site/.

The full app needs a Mistral API key for embeddings and answers, which a
static site can't hold. This demo shows the retrieval half of the pipeline:
the cleaned policy documents are chunked with the same settings as app.py
(1000 characters, 200 overlap) and searched in the browser with BM25.

Usage:
    python demo/build_static.py
"""
import hashlib
import json
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, '_site')
DATA = os.path.join(ROOT, 'data_clean')
CHUNK_SIZE, OVERLAP = 1000, 200

TITLES = {
    'Mop_UG_AY 2023-24.txt': 'UG Manual of Policies (AY 2023-24)',
    '345_Resident_Student_Policy_2025_26_NC.txt': 'Resident Student Guidelines (2025-26)',
    'MOP1.txt': 'Mass Communication Manual of Policies',
}


def file_hash(name):
    with open(os.path.join(OUT, name), 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()[:10]


def split_text(text):
    """Greedy line-based splitter, close to LangChain's RecursiveCharacterTextSplitter."""
    lines = [ln.strip() for ln in text.split('\n')]
    chunks, current = [], []
    size = 0
    for line in lines:
        if not line:
            continue
        if size + len(line) + 1 > CHUNK_SIZE and current:
            chunks.append('\n'.join(current))
            # Keep roughly OVERLAP characters of context for the next chunk.
            tail, tail_size = [], 0
            for prev in reversed(current):
                if tail_size + len(prev) > OVERLAP:
                    break
                tail.insert(0, prev)
                tail_size += len(prev) + 1
            current, size = tail, tail_size
        current.append(line)
        size += len(line) + 1
    if current:
        chunks.append('\n'.join(current))
    return chunks


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    chunks = []
    for name in sorted(os.listdir(DATA)):
        if not name.endswith('.txt'):
            continue
        with open(os.path.join(DATA, name), encoding='utf-8') as f:
            for text in split_text(f.read()):
                chunks.append({'doc': TITLES.get(name, name), 'text': text})

    with open(os.path.join(OUT, 'chunks.json'), 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, separators=(',', ':'))
    for name in ('app.js', 'style.css'):
        shutil.copy(os.path.join(ROOT, 'demo', name), os.path.join(OUT, name))

    # Version asset URLs by content so browsers pick up new builds immediately.
    js_path = os.path.join(OUT, 'app.js')
    with open(js_path, encoding='utf-8') as f:
        js = f.read()
    js = js.replace("fetch('chunks.json')", f"fetch('chunks.json?v={file_hash('chunks.json')}')")
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js)

    with open(os.path.join(ROOT, 'demo', 'index.html'), encoding='utf-8') as f:
        html = f.read()
    for name in ('app.js', 'style.css'):
        html = html.replace(f'"{name}"', f'"{name}?v={file_hash(name)}"')
    with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Built static demo with {len(chunks)} chunks in {OUT}')


if __name__ == '__main__':
    main()
