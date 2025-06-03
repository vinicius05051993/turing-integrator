from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFacePipeline

def carregar_modelo_keybert(model_id="neuralmind/bert-base-portuguese-cased"):
    from keybert import KeyBERT
    model = KeyBERT(model_id)
    return model

def extrair_palavras_chave(texto, model, n=8):
    keywords = model.extract_keywords(
        texto,
        keyphrase_ngram_range=(1, 1),
        stop_words="portuguese",
        top_n=n,
        diversity=0.5
    )
    return ",".join([kw[0] for kw in keywords])

def main():
    try:
        model = carregar_modelo_keybert()

        texto = """
        O novo modelo de linguagem lançado pela DeepSeek demonstra avanços significativos em tarefas de compreensão
        de linguagem natural, como resposta a perguntas, geração de texto e análise semântica.
        Ele é treinado com bilhões de parâmetros e mostra desempenho competitivo com os melhores modelos open-source disponíveis.
        """

        palavras_chave = extrair_palavras_chave(texto, model)
        print("Palavras-chave:", palavras_chave)

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()