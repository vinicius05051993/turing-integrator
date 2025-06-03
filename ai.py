from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFacePipeline

def carregar_modelo(model_id="unicamp-dl/ptt5-base-portuguese-vocab"):
    tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=False)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
    return tokenizer, model

def criar_pipeline_llm(tokenizer, model):
    llm_pipeline = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=50,
        do_sample=False,
    )
    return HuggingFacePipeline(pipeline=llm_pipeline)

def criar_chain(llm):
    prompt = PromptTemplate(
        input_variables=["conteudo"],
        template=(
            "Extraia as 8 palavras mais relevantes do texto a seguir. "
            "Responda apenas com as 8 palavras separadas por vírgulas, sem explicações:\n\n"
            "{conteudo}"
        )
    )
    return prompt | llm | StrOutputParser()

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

        resposta = chain.invoke({"conteudo": texto})
        print("Tags:", resposta.strip())

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()