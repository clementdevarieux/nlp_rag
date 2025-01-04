import os
import PyPDF2
import hnswlib
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
from sentence_transformers import SentenceTransformer
import torch  # Pour vérifier la disponibilité du GPU


# Étape 1 : Extraction du texte des PDFs
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text


# Étape 2 : Création de l'index avec HNSWlib
def create_hnsw_index(doc_texts, model_name="all-MiniLM-L6-v2", ef=100, M=16, device="cpu"):
    model = SentenceTransformer(model_name, device=device)  # Charger SentenceTransformer avec le GPU
    embeddings = model.encode(doc_texts, device=device)  # Calcul des embeddings sur le GPU
    dimension = embeddings.shape[1]

    # Initialiser l'index HNSWlib
    index = hnswlib.Index(space='cosine', dim=dimension)
    index.init_index(max_elements=len(doc_texts), ef_construction=ef, M=M)

    # Ajouter des éléments à l'index
    index.add_items(embeddings, list(range(len(doc_texts))))
    index.set_ef(ef)  # Paramètre pour la recherche

    return index, model


# Étape 3 : Recherche et réponse
def get_most_relevant_doc(question, index, docs, embedding_model, device="cpu"):
    question_embedding = embedding_model.encode([question], device=device)  # Calcul de l'embedding sur le GPU
    nearest_indices, _ = index.knn_query(question_embedding, k=1)
    return docs[nearest_indices[0][0]]


def main():
    # Vérifier si un GPU est disponible
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Utilisation du périphérique : {device}")

    # Spécifiez le chemin vers les PDFs
    pdf_folder = "../data/documentation/python"
    docs = []

    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith('.pdf'):
            file_path = os.path.join(pdf_folder, pdf_file)
            docs.append(extract_text_from_pdf(file_path))

    # Créez un index HNSWlib
    index, embedding_model = create_hnsw_index(docs, device=device)

    # Configurez le pipeline de question/réponse
    tokenizer = AutoTokenizer.from_pretrained("deepset/roberta-base-squad2", use_auth_token=True)
    model = AutoModelForQuestionAnswering.from_pretrained("deepset/roberta-base-squad2", use_auth_token=True).to(device)
    nlp_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer, device=0 if device == "cuda" else -1)

    # Posez une question
    question = "How to declare a variable in Python?"
    relevant_doc = get_most_relevant_doc(question, index, docs, embedding_model, device=device)
    answer = nlp_pipeline(question=question, context=relevant_doc)

    print(f"Question: {question}")
    print(f"Answer: {answer['answer']}")


if __name__ == "__main__":
    main()
