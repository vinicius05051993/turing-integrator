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
        top_p=0.9,  # Ajustado para ser mais determinístico
        max_new_tokens=40,  # Suficiente apenas para 8 palavras
        temperature=0.3,  # Reduzido para menos criatividade
        repetition_penalty=1.2  # Evita repetições
    )
    return HuggingFacePipeline(pipeline=llm_pipeline)

def criar_chain(llm):
    prompt = PromptTemplate(
        input_variables=["conteudo"],
        template=(
            "Aqui está um texto:\n\n"
            "{conteudo}\n\n"
            "Palavras-chave (exatamente 8, separadas por vírgulas):"
        )
    )
    return prompt | llm | StrOutputParser()

def processar_resposta(resposta):
    # Extrai apenas o que vem depois dos ":" e limpa
    palavras = resposta.split(":")[-1].strip()
    # Remove qualquer pontuação final e divide
    palavras = palavras.replace(".","").replace("\n","").strip()
    palavras = [p.strip() for p in palavras.split(",") if p.strip()]

    # Garante exatamente 8 palavras
    if len(palavras) > 8:
        return ",".join(palavras[:8])
    elif len(palavras) < 8:
        return ",".join(palavras + palavras[:8-len(palavras)])
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

        resposta_bruta = chain.invoke({"conteudo": texto})
        resultado = processar_resposta(resposta_bruta)
        print(resultado)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()