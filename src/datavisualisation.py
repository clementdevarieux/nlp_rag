import json
import os

import numpy as np
import matplotlib.pyplot as plt


def launch_dataviz():
    for filename in os.listdir('evaluation_files'):
        if ".json" in filename:
            with open(f'evaluation_files/{filename}', 'r') as file:
                data = json.load(file)

            rouge1 = [item['rouge1'][0] for item in data]
            rouge2 = [item['rouge2'][0] for item in data]
            rougeL = [item['rougeL'][0] for item in data]
            rougeLsum = [item['rougeLsum'][0] for item in data]
            accurateChunk = [item['isAccurateChunk'] for item in data]

            mean_rouge1 = np.mean(rouge1)
            mean_rouge2 = np.mean(rouge2)
            mean_rougeL = np.mean(rougeL)
            mean_rougeLsum = np.mean(rougeLsum)
            mean_chunk_accuracy = np.mean(accurateChunk)

            metrics = ['rouge1', 'rouge2', 'rougeL', 'rougeLsum', 'chunk_accuracy']
            means = [mean_rouge1, mean_rouge2, mean_rougeL, mean_rougeLsum, mean_chunk_accuracy]

            plt.figure(figsize=(10, 6))
            plt.bar(metrics, means, color=['blue', 'orange', 'green', 'red', 'purple'])
            plt.xlabel('Metrics')
            plt.ylabel('Average Score')
            plt.title('Average ROUGE Scores & Chunk Accuracy')
            filename_str = filename.replace("llama3.2", "llama3_2")
            plt.savefig(f"dataviz/{filename_str.split('.')[0]}.png")
            plt.show()

launch_dataviz()