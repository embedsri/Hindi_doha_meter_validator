class MatraCounter:
    def __init__(self):
        # Define Vowels and their weights
        self.short_vowels = {'अ', 'इ', 'उ', 'ऋ'}
        self.long_vowels = {'आ', 'ई', 'ऊ', 'ए', 'ऐ', 'ओ', 'औ'}
        
        # Matras (Dependent Vowels)
        self.short_matras = {'\u093f', '\u0941', '\u0943', '\u0962'} # i, u, ru, lru
        self.long_matras = {'\u093e', '\u0940', '\u0942', '\u0947', '\u0948', '\u094b', '\u094c'} # aa, ii, uu, e, ai, o, au
        
        # Modifiers
        self.virama = '\u094d'
        self.anusvara = '\u0902' # Nasal dot -> Guru
        self.visarga = '\u0903'  # Colon -> Guru
        self.chandrabindu = '\u0901' # Moon dot -> Usually Laghu
        self.nukta = '\u093c' # Nukta (dot below)

        
        # Consonants - implicitly Short 'a' unless modified
        # We assume anything else in Devanagari range is a consonant if not above
        
    def count_matras(self, text):
        """
        Calculates the total matras in the given text.
        Returns (total_count, analysis_list)
        """
        tokens = self._tokenize(text)
        weights = self._calculate_weights(tokens)
        return sum(weights), weights

    def _tokenize(self, text):
        """
        Groups characters into logical 'Aksharas' (Syllables).
        Each token is a list of characters: [Base, Matra?, Modifier?, Virama?]
        """
        tokens = []
        current_token = []
        
        for char in text:
            # Check char type
            code = ord(char)
            is_virama = (char == self.virama)
            is_modifier = (char in [self.anusvara, self.visarga, self.chandrabindu, self.nukta])
            is_matra = (char in self.short_matras or char in self.long_matras)
            
            # If it's a dependent char, append to current token
            if is_virama or is_modifier or is_matra:
                if current_token:
                    current_token.append(char)
                else:
                    # Edge case: starts with modifier? Treat as independent if needed or ignore
                    pass
            elif 0x0900 <= code <= 0x097F: # Devanagari Block (rough range)
                # It's a new Base (Consonant or Independent Vowel)
                # Push previous token
                if current_token:
                    tokens.append(current_token)
                current_token = [char]
            else:
                # Non-Devanagari (spaces, etc). Push previous, ignore this (or handle space?)
                # Spaces reset word boundaries but metering usually flows through?
                # Actually, standard Doha meter checking ignores spaces for weight, 
                # BUT "Guru before conjunct" usually applies within a word.
                # If a word ends in Laghu and next word starts with Conjunct, does it become Guru?
                # YES, in Sanskrit/Hindi prosody, the rule often crosses word boundaries.
                if current_token:
                    tokens.append(current_token)
                    current_token = []
        
        if current_token:
            tokens.append(current_token)
            
        return tokens

    def _calculate_weights(self, tokens):
        """
        Calculates weights for tokens, handling the Conjunct (Virama) rule.
        """
        # Pass 1: Base weights
        token_weights = []
        is_conjunct = [] # True if token effectively transfers weight (has halant)
        
        for token in tokens:
            base_char = token[0]
            chars = set(token)
            
            w = 1 # Default Laghu
            
            # Check for Virama (Halant) -> Conjunct
            if self.virama in token:
                token_weights.append(0)
                is_conjunct.append(True)
                continue
            
            is_conjunct.append(False)
            
            # Check independent long vowel
            if base_char in self.long_vowels:
                w = 2
            
            # Check attached long matras
            for m in self.long_matras:
                if m in chars:
                    w = 2
                    break
            
            # Check Modifiers (Anusvara, Visarga force Guru)
            if self.anusvara in chars or self.visarga in chars:
                w = 2
                
            token_weights.append(w)
            
        # Pass 2: Adjust for Conjuncts
        # If Token i is Conjunct (weight 0), and Token i-1 exists and is Laghu (1), promote i-1 to 2.
        
        final_weights = list(token_weights)
        for i in range(1, len(final_weights)):
            if is_conjunct[i]:
                # The generic "Guru before conjunct" rule
                prev = i - 1
                if final_weights[prev] == 1:
                    final_weights[prev] = 2
                    
        return final_weights
