# Banking Knowledge Assistant

An AI-powered Banking Knowledge Assistant built using FastAPI, LangChain, ChromaDB, Hugging Face Embeddings, and Ollama.

## Features

- Upload banking policy PDFs
- Process and chunk documents
- Generate embeddings
- Store vectors in ChromaDB
- Retrieve relevant information using semantic search
- Generate contextual answers using RAG (Retrieval-Augmented Generation)

## Tech Stack

- Python
- FastAPI
- LangChain
- ChromaDB
- Hugging Face Embeddings
- Ollama (Llama 3.2)
- Streamlit

## Project Structure

```text
app/
│
├── main.py
├── rag.py
├── vectorstore.py
├── embedding.py
├── chunking.py
└── models.py

ui/
└── streamlit_app.py
```

## Installation

```bash
pip install -r requirements.txt
```

## Run FastAPI

```bash
uvicorn app.main:app --reload
```

## Run Streamlit UI

```bash
streamlit run ui/streamlit_app.py
```

## Future Enhancements

- Multi-PDF support
- Chat history
- Advanced retrieval
- Production deployment

## Author

Nisha