import re
import string
import importlib.resources

def load(resource='stopwords.txt'):
    try:
        with importlib.resources.open_text(__package__, resource, encoding='utf-8') as f:
            stopwords = {line.strip().lower() for line in f if line.strip()}
        return stopwords
    except (FileNotFoundError, ImportError) as e:
        raise FileNotFoundError(f"Stopwords resource not found: {resource}") from e

def remove(sentence, stopwords):
    tokens = re.findall(r'\w+|[^\w\s]', sentence, re.UNICODE)
    cleaned_tokens = []
    for token in tokens:
        if token.lower() not in stopwords:
            cleaned_tokens.append(token)
    while cleaned_tokens and cleaned_tokens[0] in string.punctuation:
        cleaned_tokens.pop(0)
    if not cleaned_tokens:
        return ""
    result = cleaned_tokens[0]
    for i in range(1, len(cleaned_tokens)):
        current_token = cleaned_tokens[i]
        prev_token = cleaned_tokens[i - 1]
        if (prev_token not in string.punctuation and current_token not in string.punctuation) or \
           (prev_token in string.punctuation and prev_token not in '"\'([{'):
            result += ' '
        result += current_token
        result = result[0].upper() + result[1:]
    return result