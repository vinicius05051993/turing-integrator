from keybert import KeyBERT
from transformers import AutoModel, AutoTokenizer
import torch

# 1. Configuração dos modelos disponíveis
MODELOS = {
    "portugues": "neuralmind/bert-base-portuguese-cased",  # Modelo base mais estável
    "large": "neuralmind/bert-large-portuguese-cased",     # Modelo large (mais recursos)
    "multilingue": "bert-base-multilingual-cased"          # Fallback multilíngue
}

def carregar_modelo_pt(modelo="portugues"):
    """Carrega o modelo com tratamento especial para PT-BR"""
    try:
        # Configuração especial para evitar warnings
        model = AutoModel.from_pretrained(
            MODELOS[modelo],
            output_hidden_states=True  # Melhor para extração de keywords
        )
        tokenizer = AutoTokenizer.from_pretrained(MODELOS[modelo])
        return KeyBERT(model=model, tokenizer=tokenizer)
    except Exception as e:
        print(f"Erro: {e}\nUsando fallback...")
        return KeyBERT()  # Usa modelo padrão se falhar

def extrair_keywords(texto, modelo, n=8):
    """Extrai keywords com tratamento robusto"""
    kw_model = carregar_modelo_pt(modelo)

    keywords = kw_model.extract_keywords(
        texto,
        keyphrase_ngram_range=(1, 2),
        stop_words="portuguese",
        top_n=n,
        use_mmr=True,
        diversity=0.6
    )
    return ", ".join([kw[0] for kw in keywords])

# Exemplo de uso
texto = """
O novo modelo de linguagem lançado pela DeepSeek demonstra avanços significativos...
"""

# Extrai palavras-chave (usando modelo base como padrão)
palavras_chave = extrair_keywords(texto, "portugues")
print(f"Palavras-chave: {palavras_chave}")