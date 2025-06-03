from keybert import KeyBERT
from transformers import BertModel, BertTokenizer
import torch

def carregar_modelo_keybert():
    """Carrega o modelo com configurações específicas para português"""
    try:
        # Modelo BERTimbau base (garantido para PT-BR)
        model_name = "neuralmind/bert-base-portuguese-cased"
        tokenizer = BertTokenizer.from_pretrained(model_name)
        model = BertModel.from_pretrained(model_name)
        return KeyBERT(model=model)
    except Exception as e:
        print(f"Erro ao carregar modelo: {e}")
        return KeyBERT()  # Fallback para modelo padrão

def extrair_palavras_chave(texto, n=8):
    """Função robusta para extração de keywords"""
    # Pré-processamento básico
    texto = texto.replace("\n", " ").strip()

    # Carrega o modelo
    kw_model = carregar_modelo_keybert()

    # Extração com parâmetros otimizados
    keywords = kw_model.extract_keywords(
        texto,
        keyphrase_ngram_range=(1, 2),
        stop_words="portuguese",
        top_n=n,
        use_mmr=True,
        diversity=0.6,
        nr_candidates=20
    )
    return ", ".join([kw[0] for kw in keywords])

# Exemplo de uso
texto = """
A inteligência artificial está transformando radicalmente o mercado de trabalho,
especialmente na área de tecnologia da informação. Grandes empresas como Google,
Microsoft e OpenAI desenvolvem soluções inovadoras diariamente.
"""

palavras_chave = extrair_palavras_chave(texto)
print("Palavras-chave:", palavras_chave)