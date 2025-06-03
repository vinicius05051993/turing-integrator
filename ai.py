from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def carregar_modelo(model_id="mistralai/Mistral-7B-Instruct-v0.1"):
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype="auto"
    )
    return tokenizer, model

def criar_pipeline_llm(tokenizer, model):
    llm_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device_map="auto",
        do_sample=True,
        top_p=0.9,
        max_new_tokens=50,
        temperature=0.7
    )
    return HuggingFacePipeline(pipeline=llm_pipeline)

def criar_chain(llm):
    prompt = PromptTemplate(
        input_variables=["conteudo"],
        template=(
            "Extraia as 8 palavras mais relevantes deste texto, "
            "considerando seu significado e importância. "
            "Retorne APENAS as 8 palavras separadas por vírgulas, "
            "sem nenhum texto adicional ou explicação.\n\n"
            "Texto: {conteudo}\n\n"
            "Resposta:"
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
        print("Resposta crua da LLM:")
        print(resposta)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()