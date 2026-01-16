from .meter import MatraCounter
from .text_utils import normalize_text, clean_for_counting
import re

def validate_doha(raw_text):
    """
    Validates if the text is a valid Doha.
    Returns (is_valid, report_string)
    """
    # Normalize (Urdu -> Hindi, etc)
    try:
        text = normalize_text(raw_text)
    except ImportError as e:
        return False, str(e)
    
    mc = MatraCounter()
    
    # Split into Charans (parts)
    # Typically a Doha has 4 charans. Separated by comma, pipe, or newlines.
    # Structure:
    # 13 matras, 11 matras
    # 13 matras, 11 matras
    
    # Strategy: Split by | (danda) and newlines
    # Also handle commas if explicitly used as separators in single line?
    # Let's try to identify 4 non-empty chunks.
    
    parts = re.split(r'[\|\n]+', text)
    parts = [p.strip() for p in parts if p.strip()]
    
    # If we have 2 lines, try splitting by comma?
    if len(parts) == 2:
        # Try splitting each line by comma
        new_parts = []
        for p in parts:
            subs = p.split(',')
            if len(subs) == 2:
                new_parts.extend(subs)
            else:
                new_parts.append(p)
        parts = new_parts
        
    # Ideally we have 4 charans
    if len(parts) != 4:
        return False, f"Could not split into 4 Charans. Found {len(parts)} parts using separators (|, newline, comma). Format expected: 'Charan1, Charan2 | Charan3, Charan4 ||'"
        
    expected_counts = [13, 11, 13, 11]
    results = []
    total_valid = True
    
    report = ["Analysis:"]
    
    for i, part in enumerate(parts):
        cleaned = clean_for_counting(part)
        count, weights = mc.count_matras(cleaned)
        
        is_ok = (count == expected_counts[i])
        status = "OK" if is_ok else "MISMATCH"
        if not is_ok:
            total_valid = False
            
        report.append(f"Charan {i+1}: '{part}' -> {count} Matras (Expected {expected_counts[i]}) [{status}]")
        # report.append(f"   Weights: {weights}")
        
        # Check ending of Charan 2 and 4 (must be Guru-Laghu: 2, 1) or just Laghu at end?
        # Doha Rule: Charan 2 and 4 (11 matra lines) typically end in a Guru-Laghu (S-I) pattern (2, 1) or Laghu-Laghu (1,1)?
        # Tulsidas/Kabir Dohas: "Man(2) ka(2) pher(2,1)" -> 2,1.
        # "Hoye(2,1)"
        # Rule: The last 3 matras must not be a specific pattern? 
        # Actually strictly: End of 2nd and 4th charan should be Guru-Laghu (SI).
        
        if i in [1, 3]: # 2nd and 4th
            # Check last few weights. We need to map tokens to weights correctly.
            # Assuming weights array maps somewhat to syllables.
            # We want the last non-zero weights.
            active_weights = [w for w in weights if w > 0]
            if len(active_weights) >= 2:
                last_two = active_weights[-2:]
                if last_two != [2, 1]:
                   report.append(f"   Note: Charan {i+1} usually ends in Guru-Laghu (2, 1). Found {last_two}.")
                   # strictly this might make it invalid in high-brow contexts, but let's just warn.
    
    return total_valid, "\n".join(report)
