class Tags:
    def __init__(self):
        from keybert import KeyBERT
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

class General:
    def __init__(self):
        from llama_cpp import Llama
        self.llm = Llama(model_path="models/Phi-2.Q4_K_M.gguf", n_ctx=1024, n_threads=2)

    def get(self, context, question):
        prompt = f"""### Contexto:
        {context}
        ### Pergunta:
        {question}
        ### Resposta:"""

        return llm(prompt, max_tokens=200, stop=["###"])["choices"][0]["text"].strip()
