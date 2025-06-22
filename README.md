# IIT JEE AI Tutor

A conversational AI teacher for IIT JEE (Physics, Chemistry, Mathematics) that answers questions, explains concepts, and can reference real textbook content using Retrieval-Augmented Generation (RAG).

---

## Features
- **Conversational AI**: Friendly, subject-specific teacher for Physics, Chemistry, and Mathematics.
- **Textbook-Aware**: Ingests and references IIT JEE textbooks (PDF/TXT) for accurate, curriculum-aligned answers.
- **RAG Pipeline**: Uses semantic search to find relevant textbook passages and augments LLM responses.
- **Modern Web UI**: Clean chat interface with subject tabs, example questions, and responsive design.
- **Easy Book Upload**: Add new textbooks anytime; the AI will use them in future answers.

---

## Project Structure

```
├── app.py                  # Flask/FastAPI app entry point
├── src/
│   ├── ai_iit_teacher.py   # Main AI teacher logic
│   ├── rag_engine.py       # RAG logic: ingest, store, and retrieve textbook content
│   ├── prompts.py          # All LLM prompt templates
│   ├── memory.py           # Conversation memory logic
│   └── subject_data.py     # Example questions, topic lists, etc.
├── static/
│   ├── styles.css          # Web UI styles
│   └── script.js           # Web UI logic
├── templates/
│   └── index.html          # Main web page
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project metadata
└── README.md               # This file
```

---

## How It Works

1. **User asks a question** in the web chat.
2. **AI classifies** the question (casual or subject-related).
3. For subject questions:
    - **RAG engine** retrieves relevant textbook chunks using semantic search.
    - **LLM** receives the question + textbook context and generates a step-by-step, analogy-rich answer.
4. **Response is shown** in a styled chat bubble, with HTML formatting for clarity.

---

## Adding Textbooks

1. Place your PDF or TXT file in a known location.
2. Use the `add_textbook` function from `src/rag_engine.py`:
   ```python
   from src.rag_engine import add_textbook
   add_textbook('path/to/book.pdf', 'Book Name')
   ```
3. The book is chunked, embedded, and indexed for future retrieval.

---

## Running the Project

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Start the app:**
   ```bash
   python app.py
   ```
3. **Open your browser:**
   Go to `http://localhost:5000` (or the port shown in your terminal).

---

## Requirements
- Python 3.8+
- chromadb
- sentence-transformers
- PyMuPDF (for PDF support)
- Flask or FastAPI
- tqdm

---

## Extending/Customizing
- Add more books by calling `add_textbook`.
- Update prompt templates in `src/prompts.py` for different teaching styles.
- Adjust chunk size or embedding model in `src/rag_engine.py` as needed.

---

## License
MIT License

---

## Credits
- Built with LangChain, ChromaDB, and Sentence Transformers.
- Inspired by real IIT JEE teaching methods.
