import os
from transformers import BertTokenizer, BertForSequenceClassification

def cargar_modelo():
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
    
    # Cargar el tokenizador y el modelo
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = BertForSequenceClassification.from_pretrained(model_path)
    
    return tokenizer, model

# Ejemplo de uso
if __name__ == "__main__":
    tokenizer, model = cargar_modelo()
    print("Modelo y tokenizador cargados exitosamente.")
