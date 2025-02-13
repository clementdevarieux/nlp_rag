import json
from pathlib import Path

from src.config import TEST_DIR
from src.config import DOCUMENTS_DIR
from src.llm_query import call_llm
from src.retriever import tfidf_retriever
from src.chunk import trunkate_on_h2

import evaluate
import time

with open(TEST_DIR / 'questions_evaluation.json', 'r') as f:
    eval_json = json.load(f)

def evaluate_rag_rouge(evaluation_data,
                       retrieved_indices_func,
                       generated_response_func,
                       chunks,
                       retriever,
                       llm,
                       chunking):

    rouge_scores = []
    start_time = time.strftime("%Y%m%d-%H%M%S")
    rouge = evaluate.load('rouge')

    for data in evaluation_data:
        question = data['question']
        evaluation_indice = data['indices']
        reference_response = data['reference_response']

        retrieved_indices = retrieved_indices_func(chunks, question)

        if isinstance(retrieved_indices, int):
            retrieved_indices = [retrieved_indices]

        best_retrieved_doc = chunks[retrieved_indices[0]]
        generated_response = generated_response_func(question, best_retrieved_doc, llm=llm)

        rouge_score = rouge.compute(predictions=[generated_response], references=[reference_response], use_aggregator=False)

        print(generated_response)
        print("\n\n\n\n\n\n ref response")
        print(reference_response)


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
            # print(f)
            texts.append(f.read())

    chunks = trunkate_on_h2(texts)
    evaluate_rag_rouge(eval_json,
                       tfidf_retriever,
                       call_llm,
                       chunks,
                       "tfidf_retriever",
                       "deepseek-r1:7b",
                       "double_hashtag")


#%%
