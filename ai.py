from keybert import KeyBERT
from transformers import AutoModel
from sentence_transformers import SentenceTransformer
import torch

# Configuration of available models
MODELS = {
    "portuguese": "neuralmind/bert-base-portuguese-cased",
    "multilingual": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "legal-pt": "rufimelo/Legal-BERTimbau-sts-base-pt"
}

def load_keyword_model(model_name="portuguese"):
    """Load a keyword extraction model with proper embedding setup"""
    try:
        # Method 1: Try with SentenceTransformer first
        st_model = SentenceTransformer(MODELS[model_name])
        return KeyBERT(model=st_model)

    except Exception as e:
        print(f"Warning: {e}\nTrying alternative loading method...")
        try:
            # Method 2: Fallback to direct transformer model
            model = AutoModel.from_pretrained(MODELS[model_name])
            return KeyBERT(model=model)
        except:
            # Method 3: Ultimate fallback to default model
            print("Using default multilingual model")
            return KeyBERT()

def extract_keywords(text, model, n=8):
    """Robust keyword extraction with proper settings for Portuguese"""
    keywords = model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words="portuguese",
        top_n=n,
        use_mmr=True,
        diversity=0.6,
        nr_candidates=20  # Better for Portuguese
    )
    return ", ".join([kw[0] for kw in keywords])

# Example usage
if __name__ == "__main__":
    sample_text = """
    O novo modelo de linguagem lançado pela DeepSeek demonstra avanços significativos em tarefas de compreensão
    de linguagem natural, como resposta a perguntas, geração de texto e análise semântica.
    """

    kw_model = load_keyword_model("portuguese")
    keywords = extract_keywords(sample_text, kw_model)
    print(f"Palavras-chave: {keywords}")