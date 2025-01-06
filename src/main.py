import os
import PyPDF2
import hnswlib
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
from sentence_transformers import SentenceTransformer
import torch

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def create_hnsw_index(doc_texts, model_name="all-MiniLM-L6-v2", ef=100, M=16, device="cpu"):
    model = SentenceTransformer(model_name, device=device)
    embeddings = model.encode(doc_texts, device=device)
    dimension = embeddings.shape[1]

    index = hnswlib.Index(space='cosine', dim=dimension)
    index.init_index(max_elements=len(doc_texts), ef_construction=ef, M=M)

    index.add_items(embeddings, list(range(len(doc_texts))))
    index.set_ef(ef)

    return index, model


def get_most_relevant_doc(question, index, docs, embedding_model, device="cpu"):
    question_embedding = embedding_model.encode([question], device=device)
    nearest_indices, _ = index.knn_query(question_embedding, k=1)
    return docs[nearest_indices[0][0]]


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Utilisation du périphérique : {device}")

    pdf_folder = "../data/documentation/python"
    docs = []

    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith('.pdf'):
            file_path = os.path.join(pdf_folder, pdf_file)
            docs.append(extract_text_from_pdf(file_path))

    index, embedding_model = create_hnsw_index(docs, device=device)

    tokenizer = AutoTokenizer.from_pretrained("deepset/roberta-base-squad2", use_auth_token=True)
    model = AutoModelForQuestionAnswering.from_pretrained("deepset/roberta-base-squad2", use_auth_token=True).to(device)
    nlp_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer, device=0 if device == "cuda" else -1)

    question = "How to declare a variable in Python?"
    relevant_doc = get_most_relevant_doc(question, index, docs, embedding_model, device=device)
    answer = nlp_pipeline(question=question, context=relevant_doc)

    print(f"Question: {question}")
    print(f"Answer: {answer['answer']}")


if __name__ == "__main__":
    main()
