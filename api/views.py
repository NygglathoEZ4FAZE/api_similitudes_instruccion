from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import torch
import json
import torch.nn.functional as F
from .utils import cargar_modelo
from sklearn.feature_extraction.text import TfidfVectorizer

# Inicializa el vectorizador
vectorizer = TfidfVectorizer()

# Cargar el modelo y el tokenizador al inicio
tokenizer, model = cargar_modelo()  # Asegúrate del orden de retorno en cargar_modelo()

def get_embeddings(text_list):
    embeddings = vectorizer.transform(text_list)
    return torch.tensor(embeddings.toarray(), dtype=torch.float32)

def cosine_similarity(query_vector, result_vectors):
    similarities = F.cosine_similarity(query_vector, result_vectors, dim=-1)
    return similarities

def get_best_response(query, instrucciones, respuestas):
    if not instrucciones or not respuestas:
        return {"error": "No se proporcionaron instrucciones o respuestas."}

    vectorizer.fit(instrucciones)
    
    # Obtener embeddings de la consulta y de las instrucciones
    query_embedding = get_embeddings([query])
    result_embeddings = get_embeddings(instrucciones)

    # Asegurarse de que las dimensiones coincidan
    query_embedding = query_embedding.squeeze()
    result_embeddings = result_embeddings.squeeze()

    # Calcular la similitud coseno
    similarities = cosine_similarity(query_embedding, result_embeddings)

    # Filtrar respuestas por similitud > 0.5
    filtered_indices = [i for i, sim in enumerate(similarities) if sim >= 0.5]
    if not filtered_indices:
        return {"error": "No se encontraron respuestas con similitud superior al umbral."}

    filtered_instructions = [instrucciones[i] for i in filtered_indices]
    filtered_responses = [respuestas[i] for i in filtered_indices]

    # Realizar el ranking con el modelo
    ranking_scores = []
    for instr, resp in zip(filtered_instructions, filtered_responses):
        input_data = tokenizer.encode_plus(instr + resp, return_tensors="pt")
        logits = model(**input_data).logits[0]
        ranking_score = logits.max().item()
        ranking_scores.append(ranking_score)

    # Encontrar el índice de la mejor respuesta
    best_match_index = ranking_scores.index(max(ranking_scores))
    best_response = filtered_responses[best_match_index]

    return {
        "query": query,
        "best_response": best_response,
        "instrucciones": filtered_instructions,
    }
    
@method_decorator(csrf_exempt, name='dispatch')
class GetBestResponseView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            query = data.get("query")
            instrucciones = data.get("instrucciones", [])
            respuestas = data.get("respuestas", [])

            if not query or not instrucciones or not respuestas:
                return JsonResponse({"error": "Consulta, instrucciones o respuestas no proporcionadas."}, status=400)

            # Llama a tu función para obtener la mejor respuesta
            result = get_best_response(query, instrucciones, respuestas)

            return JsonResponse(result, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Error al decodificar JSON."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
