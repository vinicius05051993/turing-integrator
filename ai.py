from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def carregar_modelo(model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
    """Carrega o modelo e tokenizer DeepSeek R1"""
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map={"": "cpu"},
        offload_folder="./offload",  # ← cria pasta local p/ armazenar partes do modelo
        trust_remote_code=True,
        torch_dtype="auto"
    )
    return tokenizer, model

def criar_pipeline_llm(tokenizer, model):
    """Cria pipeline HuggingFace e integra com LangChain"""
    llm_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=200,
        do_sample=False
    )
    return HuggingFacePipeline(pipeline=llm_pipeline)

def criar_chain(llm):
    """Cria o encadeamento LangChain com prompt e parser"""
    prompt = PromptTemplate(
        input_variables=["conteudo"],
        template=(
            "Extraia 8 tags curtas e relevantes com base no seguinte conteúdo:\n\n"
            "{conteudo}\n\n"
            "Responda apenas com as tags, separadas por vírgulas."
        )
    )
    return prompt | llm | StrOutputParser()

def gerar_tags(texto, chain):
    """Executa o chain para gerar tags"""
    return chain.invoke({"conteudo": texto})

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
    print("Tags:", resultado)

if __name__ == "__main__":
    main()