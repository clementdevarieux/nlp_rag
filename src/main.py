from pathlib import Path

import click

from doc_scrapper.scrapper_rustdoc import CRATE_URL, main_scrap
from src.chunk import truncate_on_h2
from src.config import DOCUMENTS_DIR
from src.llm_query import call_llm
from src.prompt import build_prompt
from src.retriever import tfidf_retriever, hyde_retriever, transformers_retriever, jaccard_retriever, \
    hypothetical_query_retriever


@click.group()
def cli():
    pass


@click.command()
@click.option("--link", default=CRATE_URL, help="Enter the link to download the rust doc")
def scrap(link):
    main_scrap(link)


@click.command()
@click.option("--query", default="", help="Enter the link to download the rust doc")
@click.option("--llm", default="llama2", help="llm used by Ollama, to make it work install ollama")
@click.option("--retriever", default="tf_idf",
              help="retriever available : \n-tf_idf\njaccard\ntransformers\nhyde\nhypo")
def run(query, llm, retriever):
    retriever = (tfidf_retriever if retriever == "tf_idf" else
                 hyde_retriever if retriever == "hyde" else
                 transformers_retriever if retriever == "transformers" else
                 jaccard_retriever if retriever == "jaccard" else
                 hypothetical_query_retriever if retriever == "hypo" else
                 tfidf_retriever)

    path = Path(DOCUMENTS_DIR)

    texts = []
    for filename in path.glob("*.md"):
        with open(filename, encoding='utf-8') as f:
            texts.append(f.read())

    chunks = truncate_on_h2(texts)
    fittest_document_id = retriever(chunks, query)
    fittest_document = chunks[fittest_document_id[0]]

    prompt = build_prompt(query, fittest_document['chunk'])
    response = call_llm(prompt, llm=llm)
    print(response)


cli.add_command(scrap)
cli.add_command(run)

if __name__ == "__main__":
    cli()
