# RAG-REDIS-QDRANT

Ask questions about any PDF document and get answers powered by AI — with a semantic cache so repeated questions never hit the API twice.

---

## What does this project do?

You give it a PDF. You ask it questions. It answers using only the content inside that PDF.

If you ask the same question again (or something close to it), it returns the cached answer instantly without calling the AI API at all.

---

## How it works

```
Your Question
      │
      ▼
┌─────────────────┐
│   Redis Cache   │ ◄── similar question asked before? return instantly
└────────┬────────┘
         │ no match
         ▼
┌─────────────────┐
│  Qdrant Search  │ ◄── finds the most relevant chunks from your PDF
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Groq LLM API  │ ◄── generates a human answer from those chunks
└────────┬────────┘
         │
         ▼
    Your Answer
    (stored in Redis for next time)
```

**At startup**, the app reads your PDF, splits it into chunks, converts each chunk into a vector (a list of numbers that represents its meaning), and stores them in Qdrant.

**At query time**, your question is also converted into a vector and compared against all stored chunks. The most similar chunks are pulled out and sent to the Groq LLM to generate an answer.

**Redis sits in front of everything.** Before touching Qdrant or the LLM, it checks if a semantically similar question was already answered. If yes, it returns the cached answer immediately.

---

## Tech Stack

| What | Tool |
|------|------|
| PDF reading | PyMuPDF |
| Text → Vector conversion | SentenceTransformers (`all-MiniLM-L6-v2`) |
| Vector storage & search | Qdrant (runs in Docker) |
| LLM answer generation | Groq API |
| Semantic cache | Redis (runs in Docker) |

---

## Project Structure

```
RAG-REDIS-QDRANT/
├── main.py                  # Entry point — runs the app
├── requirements.txt
├── .env                     # Your API keys (never commit this)
├── data/
│   └── your_document.pdf
└── src/
    ├── config.py            # All settings in one place
    ├── ingestion/
    │   └── pdf_loader.py    # Reads and chunks the PDF
    ├── vectorstore/
    │   └── qdrant.py        # Stores and searches vectors
    ├── llm/
    │   └── groq.py          # Calls Groq to generate answers
    └── cache/
        └── redis.py         # Semantic cache layer
```

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/abdulsamadgilal/RAG-REDIS-QDRANT.git
cd RAG-REDIS-QDRANT
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the containers

```bash
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
docker run -d --name redis-cache -p 6379:6379 redis
```

### 3. Add your API keys

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379
```

### 4. Add your PDF

Drop your PDF into the `data/` folder and update `PDF_PATH` in `src/config.py`.

### 5. Run

```bash
python main.py
```

---

## Example

```
Ask anything about the document. Type 'exit' to quit.

You: What are Abdul's skills?
[CACHE MISS] Calling API...
Assistant: Abdul's skills include LangChain, FastAPI, OpenCV ...

You: What skills does Abdul have?
[CACHE HIT] Returning cached answer...
Assistant: Abdul's skills include LangChain, FastAPI, OpenCV ...
```

The second question is worded differently but means the same thing — Redis catches it and returns instantly.

---

## License

[LICENSE](LICENSE)
