import os
import re
from symspellpy import SymSpell, Verbosity

class SpellChecker:
    def __init__(self, language='es'):
        self.language = 'es'
        dict_path = f"./dictionaries/{language}_frequency_dictionary.txt"
        self.sym_spell = SymSpell(
            max_dictionary_edit_distance=2, 
            prefix_length=7
        )
        
        # Load Spanish frequency dictionary (Format: "word frequency")
        if os.path.exists(dict_path):
            self.sym_spell.load_dictionary(
                dict_path, term_index=0, count_index=1, separator=" ", encoding="utf-8"
            )
        else:
            raise FileNotFoundError(f"Dictionary file not found at: {dict_path}")





        
        print(f"SpellChecker initialized for language: {language}")
        trial = "escrivo mal a proposito aver que paza"
        print(f"Checking spelling for: '{trial}'")
        misspelled = self.get_misspelled_words(trial)
        print(f"Misspelled words: {misspelled}")
        for word in misspelled:
            suggestions = self.get_suggestions(word)
            print(f"Suggestions for '{word}': {suggestions}")

    def clean_text(self, text: str) -> list[str]:
        """Strip punctuation while keeping Spanish accents and characters."""
        # Removes punctuation except Spanish letters (á, é, í, ó, ú, ñ, ü)
        cleaned = re.sub(r'[^\w\sáéíóúñüÁÉÍÓÚÑÜ]', '', text)
        return cleaned.split()

    def check_word(self, word: str) -> bool:
        """Returns True if the word is spelled correctly, False otherwise."""
        # Ignore numbers or single characters
        if word.isdigit() or len(word) <= 1:
            return True
        
        # Exact match check in dictionary
        suggestions = self.sym_spell.lookup(
            word.lower(), 
            Verbosity.TOP, 
            max_edit_distance=0
        )
        print(f"Checking word: '{word}', Suggestions: {[item.term for item in suggestions]}")
        return len(suggestions) > 0

    def get_misspelled_words(self, text: str) -> list[str]:
        """Scans a block of text and returns a list of unknown/misspelled words."""
        words = self.clean_text(text)
        misspelled = []
        
        for word in words:
           
            if not self.check_word(word):
                
                misspelled.append(word)
                
        return misspelled

    def get_suggestions(self, word: str, max_suggestions: int = 5) -> list[str]:
        """Returns a list of suggested corrections for a misspelled word."""
        suggestions = self.sym_spell.lookup(
            word.lower(),
            Verbosity.CLOSEST,
            max_edit_distance=2,
            transfer_casing=True # Preserves initial capitals if present
        )
        
        return [item.term for item in suggestions[:max_suggestions]]

    def add_custom_word(self, word: str, frequency: int = 1000):
        """Add character names or Manga slang dynamically to memory."""
        self.sym_spell.create_dictionary_entry(word.lower(), frequency)
   