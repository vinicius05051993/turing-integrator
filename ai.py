from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

# 1. Modelos recomendados já otimizados para sentence-transformers
MODELOS_DISPNIVEIS = {
    "portugues": "rufimelo/Legal-BERTimbau-sts-base-pt",  # Otimizado para similaridade
    "multilingue": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "pt-keywords": "tgsc/bertimbau-keyword-extractor"  # Especializado em palavras-chave
}

def carregar_modelo(modelo="portugues"):
    # Carrega o modelo pré-otimizado
    st_model = SentenceTransformer(MODELOS_DISPNIVEIS[modelo])
    return KeyBERT(model=st_model)

def extrair_palavras_chave(texto, model, n=8):
    keywords = model.extract_keywords(
        texto,
        keyphrase_ngram_range=(1, 2),  # Captura palavras simples e compostas
        stop_words="portuguese",
        top_n=n,
        diversity=0.6,  # Garante variedade
        use_mmr=True  # Algoritmo de Maximal Marginal Relevance
    )
    return [kw[0] for kw in keywords]

def main():
    try:
        # Carrega o modelo especializado
        model = carregar_modelo("pt-keywords")

        texto = """
        O novo modelo de linguagem lançado pela DeepSeek demonstra avanços significativos em tarefas de compreensão
        de linguagem natural, como resposta a perguntas, geração de texto e análise semântica.
        Ele é treinado com bilhões de parâmetros e mostra desempenho competitivo com os melhores modelos open-source disponíveis.
        """

        palavras_chave = extrair_palavras_chave(texto, model)
        print("Palavras-chave:", ", ".join(palavras_chave))

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()