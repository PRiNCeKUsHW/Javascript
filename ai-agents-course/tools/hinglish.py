"""Hinglish narration for Kokoro's Hindi voices: Hindi (Devanagari) words keep espeak's Hindi
phonemes, and English words (Latin script, digits) are phonemized as English and then moved to
an Indian-English accent: retroflex t/d, a tapped r, v for w, pure o:/e: vowels, dental th."""
import re

LATIN = re.compile(r"[A-Za-z0-9]")
# order matters: protect affricates, then rhotic vowels, then the rest
RULES = [
    ("tʃ", "\x01"), ("dʒ", "\x02"),
    ("ɑːɹ", "aːr"), ("ɑɹ", "aːr"), ("ɔːɹ", "ɔːr"), ("ɔɹ", "ɔːr"), ("ɪɹ", "iːr"), ("ɛɹ", "eːr"),
    ("ɚ", "ər"), ("ɝ", "ər"),
    ("ɾ", "ʈ"), ("t", "ʈ"), ("d", "ɖ"),
    ("θ", "tʰ"), ("ð", "d"), ("ɹ", "r"), ("w", "ʋ"), ("v", "ʋ"),
    ("oʊ", "oː"), ("əʊ", "oː"), ("eɪ", "eː"), ("ɑː", "ɔ"), ("ɒ", "ɔ"), ("æ", "ɛ"),
    ("ʌ", "ə"), ("ɐ", "ə"), ("ᵻ", "ɪ"), ("ɔː", "ɔ"),
    ("\x01", "tʃ"), ("\x02", "dʒ"),
]


def indianize(ipa: str) -> str:
    for a, b in RULES:
        ipa = ipa.replace(a, b)
    return ipa


def phonemes(tokenizer, text: str) -> str:
    """Split into runs of English (Latin/digits) and Hindi words; phonemize each run in its language."""
    text = text.replace("।", ".")  # espeak drops the danda, and with it the sentence pause
    runs: list[tuple[bool, list[str]]] = []
    for word in text.split():
        eng = bool(LATIN.search(word))
        if runs and runs[-1][0] == eng:
            runs[-1][1].append(word)
        else:
            runs.append((eng, [word]))
    out = []
    for eng, words in runs:
        chunk = " ".join(words)
        if eng:
            out.append(indianize(tokenizer.phonemize(chunk, "en-us")))
        else:
            out.append(re.sub(r"\((en|hi)\)", "", tokenizer.phonemize(chunk, "hi")))
    return " ".join(p.strip() for p in out if p.strip())
