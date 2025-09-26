import json
import re
from utils.gemini_client import generate_gemini

def extract_metadata(text: str) -> dict:
    # Tronca il testo se troppo lungo per evitare errori di token
    if len(text) > 5000:
        text = text[:5000] + "..."
    
    prompt = f"""
Analyze the following document and extract metadata information.
Return ONLY a valid JSON object with the following structure:
{{
    "title": "document title or 'Untitled' if not found",
    "author": "author name or 'Unknown' if not found", 
    "date": "publication date in YYYY-MM-DD format or 'Unknown' if not found",
    "keywords": ["keyword1", "keyword2", "keyword3"]
}}

Important: 
- Return ONLY the JSON object, no additional text
- If information is not available, use the default values shown
- Extract 3-5 relevant keywords from the content
- Ensure all JSON strings are properly escaped

Document content:
{text[:3000]}
"""
    
    try:
        resp = generate_gemini(prompt)
        
        # Pulizia della risposta per estrarre solo il JSON
        resp_cleaned = clean_json_response(resp)
        
        # Tentativo di parsing del JSON
        metadata = json.loads(resp_cleaned)
        
        # Validazione e sanitizzazione dei dati
        validated_metadata = validate_metadata(metadata)
        
        return validated_metadata
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw response: {resp}")
        
        # Fallback: estrazione manuale delle informazioni
        return extract_metadata_fallback(text)
        
    except Exception as e:
        print(f"General error in extract_metadata: {e}")
        return {
            "title": "Extraction Error",
            "author": "Unknown", 
            "date": "Unknown",
            "keywords": ["document", "text", "content"],
            "error": f"Metadata extraction failed: {str(e)}"
        }

def clean_json_response(response: str) -> str:
    """Pulisce la risposta per estrarre solo il JSON valido"""
    # Rimuove testo prima e dopo il JSON
    response = response.strip()
    
    # Cerca il JSON tra le parentesi graffe
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    return response

def validate_metadata(metadata: dict) -> dict:
    """Valida e sanitizza i metadati estratti"""
    validated = {
        "title": str(metadata.get("title", "Untitled")).strip() or "Untitled",
        "author": str(metadata.get("author", "Unknown")).strip() or "Unknown",
        "date": str(metadata.get("date", "Unknown")).strip() or "Unknown",
        "keywords": []
    }
    
    # Validazione keywords
    keywords = metadata.get("keywords", [])
    if isinstance(keywords, list):
        validated["keywords"] = [str(k).strip() for k in keywords[:10] if str(k).strip()]
    elif isinstance(keywords, str):
        # Se keywords è una stringa, prova a splitarla
        validated["keywords"] = [k.strip() for k in keywords.split(",") if k.strip()]
    
    # Se non ci sono keywords, aggiungi alcune di default
    if not validated["keywords"]:
        validated["keywords"] = ["document", "text"]
    
    return validated

def extract_metadata_fallback(text: str) -> dict:
    """Estrazione di fallback quando il parsing JSON fallisce"""
    # Estrazione del titolo (prime righe non vuote)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    title = lines[0] if lines else "Untitled"
    
    # Limitazione lunghezza titolo
    if len(title) > 100:
        title = title[:97] + "..."
    
    # Estrazione parole chiave semplici (parole più frequenti)
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    word_freq = {}
    for word in words[:500]:  # Limita l'analisi
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Le 5 parole più frequenti come keywords
    common_words = {'the', 'and', 'that', 'have', 'for', 'not', 'with', 'you', 'this', 'but', 'his', 'from', 'they'}
    keywords = [word for word, count in sorted(word_freq.items(), key=lambda x: x[1], reverse=True) 
                if word not in common_words][:5]
    
    return {
        "title": title,
        "author": "Unknown",
        "date": "Unknown", 
        "keywords": keywords or ["document", "text"],
        "extraction_method": "fallback"
    }