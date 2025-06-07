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

    def _build_prompt(self, context, question):
        return (
            "### Instrução:\n"
            "Você é um assistente inteligente. Use o contexto abaixo para responder com clareza e precisão.\n\n"
            "### Contexto:\n"
            f"{context}\n\n"
            "### Pergunta:\n"
            f"{question}\n\n"
            "### Resposta:"
        )

    def _truncate_context(self, context, question, max_out_tokens=300, safety_margin=50):
        # monta prompt base sem contexto longo
        prompt = self._build_prompt("", question)
        # quantos tokens já ocupados (instrução + pergunta fixa)
        base_tokens = len(self.llm.tokenize(prompt.encode()))
        # espaço disponível para contexto
        avail = self.llm.n_ctx - max_out_tokens - base_tokens - safety_margin

        if avail <= 0:
            return ""  # não há espaço sobrando

        # começa com todo o contexto e vai reduzindo se preciso
        current = context
        while True:
            tok_count = len(self.llm.tokenize(current.encode()))
            if tok_count <= avail:
                return current
            # corta 10% cada vez até caber
            cut_len = int(len(current) * 0.9)
            current = current[:cut_len]

    def get(self, context, question):
        # aplica truncagem automática
        safe_ctx = self._truncate_context(context, question)
        prompt = self._build_prompt(safe_ctx, question)

        resposta = self.llm(
            prompt,
            max_tokens=300,
            stop=["###"],
            temperature=0.1,
            top_p=0.95
        )
        return resposta["choices"][0]["text"].strip()
