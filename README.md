<div align="center">

# 🎓 University Chatbot (RAG)

**An AI assistant that answers student questions from official university policy documents, using Retrieval-Augmented Generation (RAG).**

<!-- LIVE_DEMO_START -->
<!-- The live demo link will go here after deployment. -->
<!-- LIVE_DEMO_END -->

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain&logoColor=white)
![Mistral AI](https://img.shields.io/badge/Mistral_AI-FA520F?style=flat&logo=mistralai&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6F00?style=flat)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)

</div>

---

## The problem

University rules are spread across long PDF manuals covering academic regulations, hostel policies and programme guidelines. Students rarely read them, so the same questions reach faculty and administration again and again.

## The solution

This chatbot indexes the official manuals in a vector database. It answers questions **only from those documents**, which keeps answers accurate and stops the model from inventing rules. If the documents don't contain the answer, the bot says so instead of guessing.

## How it works

```
             ┌───────────────── Indexing (one-time) ─────────────────┐
 Policy docs │ clean_data.py → chunk (1000 chars, 200 overlap) →     │
 (.txt)      │ Mistral embeddings (mistral-embed) → ChromaDB         │
             └────────────────────────────────────────────────────────┘

             ┌───────────────── Query (per question) ────────────────┐
 Student  →  │ embed question → top-5 similarity search in ChromaDB → │ → Answer
 question    │ grounded prompt + context → Mistral Large (temp 0.1)   │
             └────────────────────────────────────────────────────────┘
```

1. **Clean.** `clean_data.py` strips tags, page numbers and extra blank lines from the source text.
2. **Chunk and embed.** Documents are split with LangChain's `RecursiveCharacterTextSplitter`, embedded with `mistral-embed` and saved to a persistent ChromaDB store.
3. **Retrieve.** For each question, the 5 most similar chunks are retrieved.
4. **Generate.** A LangChain (LCEL) pipeline passes the retrieved context and the question to `mistral-large-latest`. The prompt tells it to answer strictly from that context.
5. **Chat UI.** A Streamlit chat interface keeps the conversation history for the session.

## Knowledge base

| Document | Covers |
|---|---|
| UG Manual of Policies (AY 2023-24) | Academic rules, attendance, grading, examinations |
| Resident Student Guidelines (2025-26) | Hostel rules, residence policies, contacts |
| Mass Communication Manual of Policies | Programme-specific academic guidelines |

To add more sources, put `.txt` files in `data/`, run `clean_data.py`, then delete `vector_db_mistral/` so the index is rebuilt.

## Tech stack

- **LLM:** Mistral Large (`mistral-large-latest`)
- **Embeddings:** Mistral (`mistral-embed`)
- **Orchestration:** LangChain (LCEL runnables, prompt templates, output parsers)
- **Vector store:** ChromaDB (persistent)
- **UI:** Streamlit

## Getting started

**Prerequisites:** Python 3.10+ and a [Mistral API key](https://console.mistral.ai/).

```bash
git clone https://github.com/Ananyaverma132005/University-Chatbot.git
cd University-Chatbot

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt

# Optional: set the key once instead of typing it in the app
set MISTRAL_API_KEY=your_key_here         # Windows (cmd)
# export MISTRAL_API_KEY=your_key_here    # macOS / Linux

streamlit run app.py
```

If you don't set the environment variable, enter your API key in the sidebar. On Windows, you can also double-click `run_app.bat`.

A pre-built vector index (`vector_db_mistral/`) is included, so the app starts without re-embedding the documents.

## Deployment (Streamlit Community Cloud, free)

1. Sign in at [share.streamlit.io](https://share.streamlit.io) with GitHub → **Create app** → choose this repo, branch `main`, file `app.py`.
2. Under **Advanced settings → Secrets**, add:
   ```toml
   MISTRAL_API_KEY = "your_key_here"
   ```
3. Click **Deploy**. The app reads the key automatically, so visitors can chat without entering one.

## Example questions

- *What is the minimum attendance required to sit for end-term exams?*
- *What are the hostel in-time rules for UG students?*
- *How is the CGPA calculated?*

## Project structure

```
University-Chatbot/
├── app.py               # Streamlit app + RAG pipeline
├── clean_data.py        # Pre-processing for raw policy text
├── data/                # Raw source documents
├── data_clean/          # Cleaned documents (indexed)
├── vector_db_mistral/   # Persistent ChromaDB index
├── requirements.txt
└── run_app.bat          # One-click launcher (Windows)
```

## Future improvements

- Show source citations (document and section) with each answer
- Ingest PDFs directly instead of pre-converted text
- Add an evaluation set to measure retrieval and answer accuracy

## Author

**Ananya Verma** · [GitHub](https://github.com/Ananyaverma132005) · [LinkedIn](https://linkedin.com/in/ananya-verma)
