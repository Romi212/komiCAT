import os
import re
from symspellpy import SymSpell, Verbosity
from first_run import  dictionary_file
from spylls.hunspell import Dictionary
from storage.resources import get_dictionary


class SpellChecker:
    def __init__(self, language='es', termbase = None):
        self.language = language
        self.termbase = termbase
        self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)

        self.custom_words = set()      # stored lowercase
        self.ignore_words = set()
        path = dictionary_file(language)
        if not path.exists():
            raise FileNotFoundError(f"No {language} dictionary at {path}")
        self.sym_spell.load_dictionary(str(path), term_index=0, count_index=1)

        self.hunspell = Dictionary.from_files( str(get_dictionary(self.language)))   


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

        if word in self.ignore_words:
            return True
        # Exact match check in dictionary
        suggestions = self.sym_spell.lookup(
            word.lower(), 
            Verbosity.TOP, 
            max_edit_distance=0
        )
        #print(f"Checking word: '{word}', Suggestions: {[item.term for item in suggestions]}")
        return len(suggestions) > 0 or self.hunspell.lookup(word)

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
        
        suggestions = []
        closest = self.termbase.find_closest_target(word, max_distance=2)
        if closest:
            suggestions.insert(0,closest)

        for s in self.hunspell.suggest(word):
            if s not in suggestions:
                suggestions.append(s)
            if len(suggestions) >= max_suggestions + 2:     # collect a few extra to rank
                break

        # 3. SymSpell only fills gaps
        if len(suggestions) < max_suggestions:
            for item in self.sym_spell.lookup(word.lower(), Verbosity.CLOSEST,
                                            max_edit_distance=2, transfer_casing=True):
                if item.term not in suggestions:
                    suggestions.append(item.term)

        return suggestions[:max_suggestions]

    def add_custom_word(self, word, frecuency= 1000):
        self.custom_words.add(word.lower())
        self.add_custom_word_to_libraries(word)

    def ignore_word(self, word):
        self.ignore_words.add(word.lower())

    def add_custom_word_to_libraries(self, word: str, frequency: int = 1000):
        """Add character names or Manga slang dynamically to memory."""
        self.sym_spell.create_dictionary_entry(word.lower(), frequency)


    def load_custom_words(self, custom_words):
        for word in custom_words:
            self.add_custom_word(word)

    def load_ignore_words(self, ignore_words):
        for w in ignore_words:
            self.ignore_word(w)


    def get_data(self):
        return {
            "ignore_words": [w for w in self.ignore_words],
            "custom_words": {
                self.language : [w for w in self.custom_words],
            }
        }