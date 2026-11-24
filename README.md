# University Chatbot

A chatbot that answers student questions about university rules (attendance, exams, grading, hostel policy) using the official policy documents.

## Features

- Searches the university policy manuals for the sections relevant to each question
- Answers only from those documents, and says so when the answer isn't in them
- Simple chat interface

## Tech stack

Python, LangChain, Mistral, ChromaDB, Streamlit

## Run locally

```bash
git clone https://github.com/Ananyaverma132005/University-Chatbot.git
cd University-Chatbot
pip install -r requirements.txt
streamlit run app.py
```

Enter your Mistral API key in the sidebar, or set `MISTRAL_API_KEY` first.

## Live demo

https://ananyaverma132005.github.io/University-Chatbot/
