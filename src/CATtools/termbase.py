
def _levenshtein(a, b):
    if len(a) < len(b):
        a, b = b, a
    prev_row = range(len(b) + 1)
    for i, ca in enumerate(a, 1):
        curr_row = [i]
        for j, cb in enumerate(b, 1):
            insert_cost = curr_row[j - 1] + 1
            delete_cost = prev_row[j] + 1
            replace_cost = prev_row[j - 1] + (ca != cb)
            curr_row.append(min(insert_cost, delete_cost, replace_cost))
        prev_row = curr_row
    return prev_row[-1]

class Termbase:
    def __init__(self, source_lan, target_lan):
        self.source_lan = source_lan
        self.target_lan = target_lan
        self.termbase_dict = {}
        self.reverse_termbase_dict = {}

    def add_entry(self, source_term, target_term):
        if source_term in self.termbase_dict:
            self._remove_reverse_entry(source_term, self.termbase_dict[source_term])

        self.termbase_dict[source_term] = target_term
        self.reverse_termbase_dict.setdefault(target_term, []).append(source_term)

    def look_up(self, source_term):
        return self.termbase_dict.get(source_term)

    def look_up_source(self, target_term):
        sources = self.reverse_termbase_dict.get(target_term)
        return sources[-1] if sources else None

    def remove_entry(self, source_term):
        if source_term not in self.termbase_dict:
            return False

        target_term = self.termbase_dict.pop(source_term)
        self._remove_reverse_entry(source_term, target_term)
        return True

    def source_in(self, source_term):
        return source_term in self.termbase_dict

    def _remove_reverse_entry(self, source_term, target_term):
        sources = self.reverse_termbase_dict[target_term]
        sources.remove(source_term)
        if not sources:
            del self.reverse_termbase_dict[target_term]

    def get_data(self):
        return {
            "source_lan": self.source_lan,
            "target_lan": self.target_lan,
            "termbase_dict": self.termbase_dict,
            "reverse_termbase_dict": self.reverse_termbase_dict
        }

    def load_data(self, data):
        self.source_lan = data["source_lan"]
        self.target_lan = data["target_lan"]
        self.termbase_dict = data["termbase_dict"]
        self.reverse_termbase_dict = data["reverse_termbase_dict"]

    def find_terms_in(self, text):
        """Find all termbase source terms appearing in text.
        Returns a list of (start, end, source_term, target_term), sorted by start,
        with overlapping matches resolved in favor of the longest term."""
        raw_matches = []
        for source_term, target_term in self.termbase_dict.items():
            start = 0
            while True:
                idx = text.find(source_term, start)
                if idx == -1:
                    break
                raw_matches.append((idx, idx + len(source_term), source_term, target_term))
                start = idx + 1  # allow overlapping candidates; resolved below

        # Prefer longer matches first, then earlier ones, when resolving overlaps
        raw_matches.sort(key=lambda m: (-(m[1] - m[0]), m[0]))

        resolved = []
        occupied = [False] * (len(text) + 1)
        for start, end, source_term, target_term in raw_matches:
            if any(occupied[start:end]):
                continue  # overlaps an already-accepted, longer match
            for i in range(start, end):
                occupied[i] = True
            resolved.append((start, end, source_term, target_term))

        resolved.sort(key=lambda m: m[0])
        return resolved

    def find_closest_target(self, word, max_distance=2):
        """Fuzzy-match word against known target terms. Returns the closest
        target term within max_distance, or None if nothing is close enough."""
        word_lower = word.lower()
        best_term = None
        best_distance = max_distance + 1

        for target_term in self.reverse_termbase_dict:
            distance = _levenshtein(word_lower, target_term.lower())
            if distance < best_distance:
                best_distance = distance
                best_term = target_term

        return best_term if best_term is not None else None