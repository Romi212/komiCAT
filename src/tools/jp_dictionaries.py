from jamdict import Jamdict


class JPDictionary():
    def __init__(self):
        self.jam = Jamdict()


    def lookup_jp(self,kotoba):
        print(f"looking for word {kotoba}")
        result = self.jam.lookup(kotoba)
        for word in result.entries:
            print(word)
        return result



