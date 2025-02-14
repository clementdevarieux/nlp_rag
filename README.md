# NLP RAG CLI

Ce projet est une interface en ligne de commande (CLI) pour effectuer des tâches de traitement du langage naturel (NLP) en utilisant divers retrieveurs et modèles de langage. Il est construit avec la bibliothèque `click` pour gérer les commandes CLI.

## Table des matières

- [Installation](#installation)
- [Utilisation](#utilisation)
- [Commandes disponibles](#commandes-disponibles)
- [Structure du projet](#structure-du-projet)
- [Contribuer](#contribuer)
- [Licence](#licence)

## Installation

1. **Cloner le dépôt** :

   ```bash
   git clone https://github.com/clementdevarieux/nlp_rag.git
   cd nlp-rag
   ```

2. **Créer un environnement virtuel** (recommandé) :

   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows, utilisez `venv\Scripts\activate`
   ```

3. **Installer les dépendances** :

   ```bash
   pip install -r requirements.txt
   ```

4. **Installer Ollama** :

   https://ollama.com

## Utilisation

Pour utiliser la CLI, exécutez le script `main.py` depuis le répertoire racine du projet :

```bash
python src/main.py <commande> [options]
```

## Commandes disponibles

### `scrap`

Télécharge et scrape la documentation Rust à partir d'un lien donné.

- **Options** :
  - `--link` : Lien vers la documentation Rust (par défaut : `CRATE_URL`).

- **Exemple** :

  ```bash
  python src/main.py scrap --link "https://example.com/rust-doc"
  ```

### `run`

Exécute une requête NLP en utilisant un retriever et un modèle de langage spécifiés.

- **Options** :
  - `--query` : Requête à traiter.
  - `--llm` : Modèle de langage à utiliser (par défaut : `llama2`).
  - `--retriever` : Méthode de retrieval à utiliser (options : `tf_idf`, `jaccard`, `transformers`, `hyde`, `hypo`).

- **Exemple** :

  ```bash
  python src/main.py run --query "Quelle est la capitale de la France ?" --llm "llama2" --retriever "tf_idf"
  ```

## Structure du projet

- `doc_scrapper/` : Contient les modules pour le scraping de la documentation Rust.
- `src/` : Contient le code source principal, y compris les modules pour le chunking, la configuration, les requêtes LLM, les prompts, et les retrieveurs.
- `main.py` : Point d'entrée principal de la CLI.
