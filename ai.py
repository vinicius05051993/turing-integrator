from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def carregar_modelo(model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map={"": "cpu"},
        offload_folder="./offload",
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
        top_p=0.95,
        max_new_tokens=128
    )
    return HuggingFacePipeline(pipeline=llm_pipeline)

def criar_chain(llm):
    prompt = PromptTemplate(
        input_variables=["conteudo"],
        template=(
            "Extraia 8 palavras-chave mais relevantes do conteúdo abaixo. "
            "Responda apenas com as 8 palavras separadas por vírgulas, sem texto extra:\n\n"
            "{conteudo}"
        )
    )
    return prompt | llm | StrOutputParser()

def gerar_tags(texto, chain):
    return chain.invoke({"conteudo": texto}).strip()

def main():
    tokenizer, model = carregar_modelo()
    llm = criar_pipeline_llm(tokenizer, model)
    chain = criar_chain(llm)

    texto = """
    O novo modelo de linguagem lançado pela DeepSeek demonstra avanços significativos em tarefas de compreensão
    de linguagem natural, como resposta a perguntas, geração de texto e análise semântica.
    Ele é treinado com bilhões de parâmetros e mostra desempenho competitivo com os melhores modelos open-source disponíveis.
    """

    resultado = gerar_tags(texto, chain)
    print(resultado)  # Só imprime as tags

if __name__ == "__main__":
    main()