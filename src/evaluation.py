import json
import time
from pathlib import Path

import evaluate
from tqdm import tqdm

from src.chunk import truncate_on_h2
from src.config import DOCUMENTS_DIR
from src.config import TEST_DIR
from src.llm_query import call_llm
from src.prompt import build_prompt
from src.retriever import hypothetical_query_retriever, tfidf_retriever, transformers_retriever, hyde_retriever

with open(TEST_DIR / 'questions_evaluation.json', 'r') as f:
    eval_json = json.load(f)


def evaluate_rag_rouge(evaluation_data,
                       retrieved_indices_func,
                       generated_response_func,
                       chunks,
                       retriever,
                       llm,
                       chunking):
    print(retriever + " " + llm)
    rouge_scores = []
    start_time = time.strftime("%Y%m%d-%H%M%S")
    rouge = evaluate.load('rouge')

    for data in tqdm(evaluation_data):
        question = data['question']
        evaluation_indice = data['indices']
        reference_response = data['reference_response']

        retrieved_indices = retrieved_indices_func(chunks, question)

        if isinstance(retrieved_indices, int):
            retrieved_indices = [retrieved_indices]

        best_retrieved_doc = chunks[retrieved_indices[0]]

        prompt = build_prompt(question, best_retrieved_doc)
        generated_response = generated_response_func(prompt, llm=llm)

        rouge_score = rouge.compute(predictions=[generated_response], references=[reference_response],
                                    use_aggregator=False)

        if retrieved_indices == evaluation_indice:
            rouge_score["isAccurateChunk"] = 1
        else:
            rouge_score["isAccurateChunk"] = 0

        rouge_scores.append(rouge_score)

    print(f"ROUGE Scores: {rouge_scores}")

    llm_str = llm.replace(":", "_")

    with open(f'evaluation_files/rouge_scores_{retriever}_{llm_str}_{chunking}_{start_time}.json', 'w') as f:
        json.dump(rouge_scores, f, indent=4)


def retrieved_indices_func(question):
    return [0, 2]


def generated_response_func(question):
    # Simuler la génération de la réponse
    return "La transposition d'un tenseur est une opération mathématique."


if __name__ == '__main__':
    path = Path(DOCUMENTS_DIR)

    texts = []
    for filename in path.glob("*.md"):
        with open(filename, encoding='utf-8') as f:
            texts.append(f.read())

    chunks = truncate_on_h2(texts)

    retrievers = [
        #{"fct": tfidf_retriever, "label": "tfidf"},
        #{"fct": hyde_retriever, "label": "hyde"},
        #{"fct": transformers_retriever, "label": "transformers"},
        {"fct": hypothetical_query_retriever, "label": "hypothetical"},
    ]

    llm = ["mistral-small", "llama2", "deepseek-r1"]

    for retriever in tqdm(retrievers):
        for llm in tqdm(llm, desc="llm"):
            evaluate_rag_rouge(eval_json,
                               retriever['fct'],
                               call_llm,
                               chunks,
                               retriever['label'],
                               llm,
                               "v2")

    # %%
