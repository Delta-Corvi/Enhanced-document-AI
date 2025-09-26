from better_profanity import profanity

# optional word list extension
profanity.load_censor_words()

def validate_input(text: str) -> str:
    """
    Returns the text if it is clean, otherwise raises ValueError.
    """
    if profanity.contains_profanity(text):
        raise ValueError("🚫 Input contains profanity.")
    return text

def validate_output(text: str) -> str:
    """
    Filters or flags the output.
    """
    if profanity.contains_profanity(text):
        return "⚠️ Response filtered due to inappropriate language."
    return text