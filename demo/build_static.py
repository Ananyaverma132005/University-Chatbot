"""Build the static GitHub Pages demo into _site/.

The full app needs a Mistral API key for embeddings and answers, which a
static site can't hold. This demo shows the retrieval half of the pipeline:
the cleaned policy documents are chunked with the same settings as app.py
(1000 characters, 200 overlap) and searched in the browser with BM25.

Usage:
    python demo/build_static.py
"""
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
    for name in ('index.html', 'app.js', 'style.css'):
        shutil.copy(os.path.join(ROOT, 'demo', name), os.path.join(OUT, name))
    print(f'Built static demo with {len(chunks)} chunks in {OUT}')


if __name__ == '__main__':
    main()
