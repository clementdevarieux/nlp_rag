import json
import os

import numpy as np
import matplotlib.pyplot as plt


def launch_dataviz():
    for filename in os.listdir('evaluation_files'):
        # Charger le fichier JSON
        with open(f'evaluation_files/{filename}', 'r') as file:
            data = json.load(file)

        # Extraire les valeurs des métriques
        rouge1 = [item['rouge1'][0] for item in data]
        rouge2 = [item['rouge2'][0] for item in data]
        rougeL = [item['rougeL'][0] for item in data]
        rougeLsum = [item['rougeLsum'][0] for item in data]

        # Calculer les moyennes
        mean_rouge1 = np.mean(rouge1)
        mean_rouge2 = np.mean(rouge2)
        mean_rougeL = np.mean(rougeL)
        mean_rougeLsum = np.mean(rougeLsum)

        # Créer les graphiques
        metrics = ['rouge1', 'rouge2', 'rougeL', 'rougeLsum']
        means = [mean_rouge1, mean_rouge2, mean_rougeL, mean_rougeLsum]

        plt.figure(figsize=(10, 6))
        plt.bar(metrics, means, color=['blue', 'orange', 'green', 'red'])
        plt.xlabel('Metrics')
        plt.ylabel('Average Score')
        plt.title('Average ROUGE Scores')
        plt.savefig(f"dataviz/{filename.split('.')[0]}.png")
        plt.show()

launch_dataviz()