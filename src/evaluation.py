import json
from pathlib import Path

from nltk.translate.bleu_score import sentence_bleu
from rouge import Rouge
from sklearn.metrics import precision_score, recall_score, f1_score

from src.config import TEST_DIR
from src.config import DOCUMENTS_DIR
from src.llm_query import call_llm
from src.retriever import tfidf_retriever
from src.chunk import trunkate_on_h2

with open(TEST_DIR / 'questions_evaluation.json', 'r') as f:
    eval_json = json.load(f)


## TODO make it work
def evaluate_rag(evaluation_data, retrieved_indices_func, generated_response_func, chunks):
    precision_scores = []
    recall_scores = []
    f1_scores = []
    bleu_scores = []
    rouge_scores = []

    rouge = Rouge()

    for data in evaluation_data:
        question = data['question']
        true_indices = data['indices']
        reference_response = data['reference_response']

        # Simuler la récupération et la génération
        retrieved_indices = retrieved_indices_func(chunks, question)

        if isinstance(retrieved_indices, int):
            retrieved_indices = [retrieved_indices]

        best_retrieved_doc = chunks[retrieved_indices[0]]
        generated_response = generated_response_func(question, best_retrieved_doc, llm='llama2')

        precision = precision_score(true_indices, retrieved_indices, average=None)
        recall = recall_score(true_indices, retrieved_indices, average=None)
        f1 = f1_score(true_indices, retrieved_indices, average=None)

        precision_scores.append(precision)
        recall_scores.append(recall)
        f1_scores.append(f1)

        # Évaluation de la génération
        bleu = sentence_bleu([reference_response.split()], generated_response.split())
        rouge_score = rouge.get_scores(generated_response, reference_response)[0]

        bleu_scores.append(bleu)
        rouge_scores.append(rouge_score)

    # Calculer les scores moyens
    avg_precision = sum(precision_scores) / len(precision_scores)
    avg_recall = sum(recall_scores) / len(recall_scores)
    avg_f1 = sum(f1_scores) / len(f1_scores)
    avg_bleu = sum(bleu_scores) / len(bleu_scores)
    avg_rouge = {key: sum([score[key] for score in rouge_scores]) / len(rouge_scores) for key in rouge_scores[0]}

    print(f"Average Precision: {avg_precision}")
    print(f"Average Recall: {avg_recall}")
    print(f"Average F1-Score: {avg_f1}")
    print(f"Average BLEU Score: {avg_bleu}")
    print(f"Average ROUGE Scores: {avg_rouge}")


def retrieved_indices_func(question):
    return [0, 2]


def generated_response_func(question):
    # Simuler la génération de la réponse
    return "La transposition d'un tenseur est une opération mathématique."


if __name__ == '__main__':
    path = Path(DOCUMENTS_DIR)

    texts = []
    for filename in path.glob("*.md"):
        with open(filename) as f:
            texts.append(f.read())

    chunks = trunkate_on_h2(texts)
    evaluate_rag(eval_json, tfidf_retriever, call_llm, chunks)


#%%
