from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import re

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
        top_p=0.85,
        max_new_tokens=30,
        temperature=0.2,
        repetition_penalty=1.5,
        num_return_sequences=1
    )
    return HuggingFacePipeline(pipeline=llm_pipeline)

def criar_chain(llm):
    prompt = PromptTemplate(
        input_variables=["conteudo"],
        template=(
            "Extraia as 8 palavras-chave mais importantes deste texto, "
            "seguindo rigorosamente estas regras:\n"
            "1. Apenas palavras individuais (não frases)\n"
            "2. Sem repetições\n"
            "3. Formato: palavra1,palavra2,palavra3,palavra4,palavra5,palavra6,palavra7,palavra8\n\n"
            "Texto: {conteudo}\n\n"
            "Palavras-chave:"
        )
    )
    return prompt | llm | StrOutputParser()

def processar_resposta(resposta):
    # Extrai todas as palavras separadas por vírgulas
    palavras = re.findall(r'\b[\w-]+\b', resposta.lower())

    # Remove duplicados mantendo a ordem
    palavras_unicas = []
    for p in palavras:
        if p not in palavras_unicas:
            palavras_unicas.append(p)

    # Garante exatamente 8 palavras
    if len(palavras_unicas) >= 8:
        return ",".join(palavras_unicas[:8])
    else:
        # Completa com as mais relevantes se necessário
        return ",".join(palavras_unicas + palavras_unicas[:8-len(palavras_unicas)])

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
        resultado = processar_resposta(resposta)
        print(resultado)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()