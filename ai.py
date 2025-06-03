from keybert import KeyBERT
from transformers import BertModel, BertTokenizer

def main():
    # 1. Carrega o modelo BERTimbau diretamente
    model_name = "neuralmind/bert-base-portuguese-cased"
    model = BertModel.from_pretrained(model_name)
    kw_model = KeyBERT(model=model)

    # 2. Texto para análise
    texto = """
    "Há necessidade, além disso, para eficácia da medida requerida e igualmente assegurar a aplicação da lei penal, de inclusão do nome da parlamentar requerida na difusão vermelha da INTERPOL, com a suspensão de seu passaporte e imediata comunicação aos países", completa Gonet, que pediu ainda o sequestro e indisponibilidade de bens da parlamentar.
    Para a PGR, a deputada deve ser considerada foragida "por ter se evadido para outro país e anunciado publicamente sua permanência na Europa e a transgressão da decisão condenatória proferida pela mais alta Corte do país, em que secominou pena a ser cumprida inicialmente em regime fechado."
    Há 20 dias, a parlamentar foi condenada por unanimidade pela Primeira Turma do Supremo Tribunal Federal (STF) a 10 anos de prisão pela invasão aos sistemas do Conselho Nacional de Justiça (CNJ).
    Em 2023, Zambelli chegou a ter o passaporte apreendido durante as investigações, mas o documento foi devolvido e ela não tinha restrições para deixar o país. No último dia 25, ela deixou o Brasil pela fronteira com a Argentina e se dirigiu para Buenos Aires, de onde voou para os Estados Unidos.
    Ministros do STF ouvidos pela GloboNews viram na saída de Zambelli do país uma fuga para tentar evitar os resultados do julgamento.
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