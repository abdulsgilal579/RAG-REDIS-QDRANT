
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)

def search_and_answer(chunks, query):
    context = "\n\n".join(chunks)

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer the question based only on the provided context."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}"
            }
        ]
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    search_and_answer("What are the skills and experience of this person?")