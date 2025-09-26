from utils.gemini_client import generate_gemini

def answer(context: str, question: str) -> str:
    prompt = f"Context:\n{context}\n\nQuestion: {question}"
    return generate_gemini(prompt)