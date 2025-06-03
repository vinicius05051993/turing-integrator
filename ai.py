from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFacePipeline

def carregar_modelo(model_id="unicamp-dl/ptt5-base-portuguese-vocab"):
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        use_fast=False,
        legacy=False  # Prevents tokenizer conversion issues
    )
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_id,
        device_map="auto"  # Better hardware utilization
    )
    return tokenizer, model

def criar_pipeline_llm(tokenizer, model):
    llm_pipeline = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=64,  # Increased slightly for better results
        do_sample=True,  # Changed to True for better diversity
        temperature=0.7,  # Added for better control
        top_p=0.9,  # Added for better quality
        num_beams=4,  # Better for keyword extraction
        early_stopping=True  # Prevent incomplete outputs
    )
    return HuggingFacePipeline(pipeline=llm_pipeline)

def criar_chain(llm):
    prompt = PromptTemplate(
        input_variables=["conteudo"],
        template=(
            "Extraia exatamente 8 palavras-chave únicas e relevantes do texto abaixo. "
            "Retorne APENAS as palavras separadas por vírgulas, sem números, pontuação ou texto adicional. "
            "Exemplo: palavra1,palavra2,palavra3,palavra4,palavra5,palavra6,palavra7,palavra8\n\n"
            "Texto: {conteudo}\n\n"
            "Palavras-chave:"
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
        # Basic cleaning while keeping the raw output structure
        resposta_limpa = resposta.strip().replace('\n', '').replace('"', '')
        print("Palavras-chave:", resposta_limpa)

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()