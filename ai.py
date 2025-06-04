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
        self.n_ctx = 1024
        self.max_response_tokens = 200
        self.llm = Llama(model_path="models/Phi-2.Q4_K_M.gguf", n_ctx=self.n_ctx, n_threads=2)

    def truncate_context(self, prompt_prefix, context, question):
        # Cria um prompt temporário para calcular os tokens ocupados antes do contexto
        base_prompt = f"{prompt_prefix}\n\n### Pergunta:\n{question}\n### Resposta:"
        base_tokens = len(self.llm.tokenize(base_prompt.encode("utf-8")))
        available_tokens = self.n_ctx - self.max_response_tokens - base_tokens

        # Trunca o contexto para caber no espaço restante
        context_tokens = self.llm.tokenize(context.encode("utf-8"))[:available_tokens]
        truncated_context = self.llm.detokenize(context_tokens).decode("utf-8", errors="ignore")
        return truncated_context

    def get(self, context, question):
        prompt_prefix = "### Contexto:"
        context = self.truncate_context(prompt_prefix, context, question)

        prompt = f"""{prompt_prefix}
        {context}
        ### Pergunta:
        {question}
        ### Resposta:"""

        output = self.llm(prompt, max_tokens=self.max_response_tokens, stop=["###"])
        return output["choices"][0]["text"].strip()
