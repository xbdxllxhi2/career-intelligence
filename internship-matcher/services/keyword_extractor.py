import spacy

nlp = spacy.load("fr_core_news_sm")

STOPWORDS =nlp.Defaults.stop_words

def extract_keywords(text: str):
    doc = nlp(text.lower())
    tokens = [
        token.lemma_
        for token in doc
        if token.pos_ in {"NOUN", "PROPN", "VERB"} and token.text not in STOPWORDS
    ]
    return sorted(set(tokens))
