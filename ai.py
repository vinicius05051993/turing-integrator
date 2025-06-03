from keybert import KeyBERT
from transformers import BertModel, BertTokenizer

def main():
    # 1. Carrega o modelo BERTimbau diretamente
    model_name = "neuralmind/bert-base-portuguese-cased"
    model = BertModel.from_pretrained(model_name)
    kw_model = KeyBERT(model=model)

    # 2. Texto para análise
    texto = """
    O novo modelo de linguagem lançado pela DeepSeek demonstra avanços significativos
    em processamento de linguagem natural para o português brasileiro.
    """

    # 3. Extração direta das palavras-chave
    keywords = kw_model.extract_keywords(
        texto,
        keyphrase_ngram_range=(1, 1),
        stop_words=None,
        top_n=8
    )

    # 4. Exibe o retorno cru do KeyBERT
    print("Retorno bruto do KeyBERT:")
    print(keywords)

    # 5. Formatação mínima (apenas para visualização)
    print("\nPalavras-chave formatadas:")
    print(", ".join([kw[0] for kw in keywords]))

if __name__ == "__main__":
    main()