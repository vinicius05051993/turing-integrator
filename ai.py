from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFacePipeline
import os

def carregar_modelo(model_id="unicamp-dl/ptt5-base-portuguese-vocab"):
    # Force using the slow tokenizer to avoid conversion issues
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        use_fast=False,  # Critical - uses slow tokenizer
        legacy=False,    # Prevents automatic conversion attempts
        local_files_only=False  # Ensures it can download if needed
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
        max_new_tokens=50,
        do_sample=False,
        clean_up_tokenization_spaces=True  # Helps with output formatting
    )
    return HuggingFacePipeline(pipeline=llm_pipeline)

def criar_chain(llm):
    prompt = PromptTemplate(
        input_variables=["conteudo"],
        template=(
            "Extraia exatamente 8 palavras-chave do texto. "
            "Apenas as palavras separadas por vírgulas, sem explicações. "
            "Exemplo: palavra1,palavra2,palavra3,palavra4,palavra5,palavra6,palavra7,palavra8\n\n"
            "Texto: {conteudo}"
        )
    )
    return prompt | llm | StrOutputParser()

def main():
    try:
        # Set cache location if needed
        os.environ['HF_HOME'] = os.path.expanduser('~/.cache/huggingface')

        tokenizer, model = carregar_modelo()
        llm = criar_pipeline_llm(tokenizer, model)
        chain = criar_chain(llm)

        texto = """
        O novo modelo de linguagem lançado pela DeepSeek demonstra avanços significativos em tarefas de compreensão
        de linguagem natural, como resposta a perguntas, geração de texto e análise semântica.
        Ele é treinado com bilhões de parâmetros e mostra desempenho competitivo com os melhores modelos open-source disponíveis.
        """

        resposta = chain.invoke({"conteudo": texto})
        print("Palavras-chave:", resposta.strip())

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()