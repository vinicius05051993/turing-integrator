import os
os.environ["LLAMA_LOG_LEVEL"] = "ERROR"

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
        self.llm = Llama(
            model_path="models/OpenHermes-2.5-Mistral.Q4_K_M.gguf",
            n_ctx=4096,
            n_threads=4,
            verbose=False
        )

    def get(self, context, question):
        try:
            context = context[:10000]
            prompt = f"""### Instrução:
            Você é um assistente inteligente. Use o contexto abaixo para responder com clareza e precisão.

            ### Contexto:
            {context}

            ### Pergunta:
            {question}

            ### Resposta:"""

            resposta = self.llm(
                prompt,
                max_tokens=300,
                stop=["###"],
                temperature=0.3,
                top_p=0.95
            )

            return resposta["choices"][0]["text"].strip()
        except Exception as e:
            return ''
