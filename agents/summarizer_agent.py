from utils.gemini_client import generate_gemini

def summarize(text: str) -> str:
    prompt = f"Summarize the following document:\n\n{text}"
    return generate_gemini(prompt)