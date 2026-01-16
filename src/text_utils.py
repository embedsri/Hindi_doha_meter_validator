import re

try:
    from aksharamukha import transliterate
    AKSHARAMUKHA_AVAILABLE = True
except ImportError:
    AKSHARAMUKHA_AVAILABLE = False

def is_urdu_script(text):
    """Checks if the text contains Urdu/Arabic characters."""
    # Basic check for Arabic Unicode block
    for char in text:
        if '\u0600' <= char <= '\u06FF':
            return True
    return False

def normalize_text(text):
    """
    Normalizes text to Devanagari script for metering.
    - Transliterates Urdu to Devanagari if needed.
    - Removes punctuation and whitespace from ends.
    """
    text = text.strip()
    
    if is_urdu_script(text):
        if not AKSHARAMUKHA_AVAILABLE:
            raise ImportError("aksharamukha library is required for Urdu support. Please install it.")
        # Transliterate Urdu to Devanagari
        # Output is usually detailed, we want standard Devanagari
        text = transliterate.process('Urdu', 'Devanagari', text)
    
    # Remove common punctuation but keep lines/pipes
    # We want to keep characters relevant for metering
    # Removing non-devanagari punctuation (except | which is Danda)
    
    # Simple cleanup: Remove anything that's not Devangari or Whitespace or Danda
    # But wait, we need to be careful not to remove valid chars.
    # For now, just return valid text.
    return text

def clean_for_counting(text):
    """Removes all non-meterable characters (spaces, punctuation) except specific ones if needed."""
    # We need to maintain word structure? 
    # Actually metering is usually per-charan, ignoring spaces in strict count?
    # No, spaces break words, but usually don't have weight.
    # We remove punctuation like commas, quotes.
    # We keep Danda (|) as generic delimiter if present, but usually we split by it before this.
    
    # Remove all standard punctuation
    cleaned = re.sub(r'[,\.\-\?\!\"\']', '', text)
    return cleaned
