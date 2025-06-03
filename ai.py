from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFacePipeline

def carregar_modelo(model_id="unicamp-dl/ptt5-base-portuguese-vocab"):
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        use_fast=False,
        legacy=False
    )
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_id,
        device_map="auto"
    )
    return tokenizer, model

def criar_pipeline_llm(tokenizer, model):
    llm_pipeline = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=40,  # Reduzido para respostas mais curtas
        do_sample=False,
        num_beams=4,  # Melhora a qualidade da extração
        early_stopping=True
    )
    return HuggingFacePipeline(pipeline=llm_pipeline)

def criar_chain(llm):
    prompt = PromptTemplate(
        input_variables=["conteudo"],
        template=(
            "texto: {conteudo}\n\n"
            "extraia 8 palavras-chave deste texto, separadas por vírgulas, sem explicações:"
        )
    )
    return prompt | llm | StrOutputParser()

def processar_resposta(resposta):
    # Filtra apenas o que vem depois dos ":" e limpa
    palavras = resposta.split(":")[-1].strip()
    # Remove pontuação indesejada
    palavras = palavras.replace(".", "").replace('"', '').strip()
    return palavras

def main():
    try:
        tokenizer, model = carregar_modelo()
        llm = criar_pipeline_llm(tokenizer, model)
        chain = criar_chain(llm)

        texto = """
        O novo modelo de linguagem lançado pela DeepSeek demonstra avanços significativos em tarefas de compreensão
        de linguagem natural, como resposta a perguntas, geração de texto e análise semântica.
        Ele é treinado com bilhões de parâmetros e mostra desempenho competitivo com os melhores modelos open-source disponíveis.
        """

        resposta_bruta = chain.invoke({"conteudo": texto})
        resposta_final = processar_resposta(resposta_bruta)

        print("Palavras-chave:", resposta_final)

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()