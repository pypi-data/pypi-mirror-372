import re

def wordTokenize(text: str):
    az_letters = "A-Za-zÇçƏəĞğİıÖöŞşÜü"
    pattern = re.compile(rf"""
        (?:https?://[^\s]+)
      | (?:www\.[^\s]+)
      | (?:[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9-.]+)
      | (?:\d{{1,3}}(?:,\d{{3}})*(?:\.\d+)?%?)
      | (?:[{az_letters}\u0400-\u04FF]+(?:['’\-][{az_letters}\u0400-\u04FF]+)*)
      | (?:\.\.\.)
      | (?:[!?.,;:\"“”'()\[\]{{}}<>—–-])
      | (?:\S)
    """, re.VERBOSE | re.UNICODE)
    return pattern.findall(text)

def sentenceTokenize(text: str):
    abbreviations = [
        "cən.", "xan.", "dr.", "prof.", "akad.", "müəll.",
        "b.e.", "b.i.", "m.e.", "m.f.", "fəls.dok.", "elm.dok.",
        "ko.", "kor.", "dəq.", "san.", "a.m.", "p.m.",
        "yan.", "fev.", "mart.", "apr.", "may.", "iyn.", "iyl.", "avq.", "sen.", "okt.", "noy.", "dek.",
        "pr.", "küç.", "ş.", "ray.", "m.", "qəs.", "mt.",
        "s.", "c.", "nömr.", "şək.", "təqr.", "təx.", "red.",
        "prez.", "naz.", "qub.", "hörm.", "məs.", "mis.", "fiq.",
        "kap.", "may.", "gen.", "polk.", "leyt.", "serj.", "kom.", "adm.", "və s.", "və i.", "və b.",
    ]

    pattern = re.compile(r'(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-öø-ÿ\u0400-\u04FF])')
    sentences = []
    for sent in re.split(pattern, text.strip()):
        sent = sent.strip()
        if not sent:
            continue
        if sentences and any(sentences[-1].lower().endswith(abbr) for abbr in abbreviations):
            sentences[-1] += ' ' + sent
        else:
            sentences.append(sent)
    return sentences

def tweetTokenize(text, reduce_len=True, remove_mentions=False):
    if remove_mentions:
        text = re.sub(r'@\w+', '', text)
    
    emoticon_str = r"""
        (?:
          [<>]?
          [:;=8]
          [\-o\*\']?
          [\)\]\(\[dDpP/:}{@|\\]
          |
          [\)\]\(\[dDpP/:}{@|\\]
          [\-o\*\']?
          [:;=8]
          [<>]?
        )"""
    
    regex_str = [
        r'https?://\S+',
        r'@\w+',
        r'\#\w+',
        emoticon_str,
        r'\w+(?:\'\w+)?',
        r'(?:\.\.\.|…)',
        r'[!?.]+',
        r'[^\s\w]'
    ]
    
    tokens = re.findall('|'.join(regex_str), text, re.VERBOSE | re.I | re.UNICODE)
    tokens = [t for t in tokens if t.strip()]
    
    if reduce_len:
        tokens = [re.sub(r'(.)\1{2,}', r'\1\1', t) for t in tokens]
    
    return tokens