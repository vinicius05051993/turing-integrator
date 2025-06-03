from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def carregar_modelo(model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
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
        top_p=0.95,
        max_new_tokens=50,  # Reduzido para evitar respostas muito longas
        temperature=0.7
    )
    return HuggingFacePipeline(pipeline=llm_pipeline)

def criar_chain(llm):
    prompt = PromptTemplate(
        input_variables=["conteudo"],
        template=(
            "Extraia as 8 palavras-chave mais relevantes do texto abaixo. "
            "Responda APENAS com 8 palavras separadas por vírgulas, SEM números, pontos ou texto adicional.\n\n"
            "Exemplo: palavra1,palavra2,palavra3,palavra4,palavra5,palavra6,palavra7,palavra8\n\n"
            "Texto: {conteudo}"
        )
    )
    return prompt | llm | StrOutputParser()

def gerar_tags(texto, chain):
    resposta = chain.invoke({"conteudo": texto}).strip()
    # Processamento extra para garantir exatamente 8 palavras
    palavras = [p.strip() for p in resposta.split(",") if p.strip()]
    if len(palavras) > 8:
        palavras = palavras[:8]  # Pega apenas as 8 primeiras
    elif len(palavras) < 8:
        # Se tiver menos de 8, completa com as mais relevantes repetidas (evitando erro)
        palavras = palavras + palavras[:8-len(palavras)]
    return ",".join(palavras)

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

        resultado = gerar_tags(texto, chain)
        print(resultado)  # Saída será exatamente 8 palavras separadas por vírgulas

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()