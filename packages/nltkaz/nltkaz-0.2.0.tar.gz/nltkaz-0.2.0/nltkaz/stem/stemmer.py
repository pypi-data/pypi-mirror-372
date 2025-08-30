import re
import bisect
import importlib.resources

class Stemmer:
    def __init__(self, keyboard="az"):
        if keyboard == "az":
            resource = 'azwords.txt'
        elif keyboard == "en":
            resource = 'enwords.txt'
        else:
            raise ValueError("Invalid keyboard. Choose 'az' or 'en'.")
        try:
            with importlib.resources.open_text(__package__, resource, encoding='utf-8') as file:
                self.roots = sorted(line.strip() for line in file if line.strip())
        except (FileNotFoundError, ImportError) as e:
            raise FileNotFoundError(f"Could not load resource file: {resource}") from e

    def _find_root(self, word):
        for i in range(len(word), 0, -1):
            prefix = word[:i]
            idx = bisect.bisect_left(self.roots, prefix)
            if idx < len(self.roots) and self.roots[idx] == prefix:
                return prefix
        return word

    def stem(self, text):
        words = re.findall(r"\w+|[^\w\s]", text)
        result = []
        for i, word in enumerate(words):
            if not word.isalpha():
                if result:
                    result[-1] = result[-1].rstrip() + word + ' '
                else:
                    result.append(word + ' ')
            else:
                stemmed = self._find_root(word.lower())
                result.append(stemmed + ' ')
        text = "".join(result).strip()
        return re.sub(r"\s+", " ", text)