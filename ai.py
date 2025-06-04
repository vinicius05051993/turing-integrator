from keybert import KeyBERT

class Tags:
    def __init__(self):
        model_name = "sentence-transformers/distiluse-base-multilingual-cased-v2"
        self.kw_model = KeyBERT(model=model_name)

    def get(self, texto, n=8, diversity=0.1):
        return self.kw_model.extract_keywords(
            texto.lower(),
            keyphrase_ngram_range=(1, 1),
            stop_words=None,
            top_n=n,
            use_mmr=True,
            diversity=diversity
        )
