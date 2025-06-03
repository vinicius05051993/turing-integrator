from keybert import KeyBERT
from transformers import BertModel, BertTokenizer

class Tags:
    def __init__(self):
        model_name = "neuralmind/bert-large-portuguese-cased"
        self.model = BertModel.from_pretrained(model_name)
        self.kw_model = KeyBERT(model=self.model)

    def get(self, texto, n=8):
        return self.kw_model.extract_keywords(
            texto,
            keyphrase_ngram_range=(1, 1),
            stop_words=None,
            top_n=n
        )