import os
from dotenv import load_dotenv

load_dotenv()

PDF_PATH = "data/Abdul Samad Gilal Resume.pdf"
COLLECTION_NAME = "pdf_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "openai/gpt-oss-120b"
