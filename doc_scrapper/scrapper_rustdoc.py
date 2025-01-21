import requests
from bs4 import BeautifulSoup
import re
import os

BASE_URL = "https://docs.rs"
CRATE_URL = "https://docs.rs/burn/latest/burn/index.html"

def to_markdown(html_content):
    """
    Convertit rapidement (et de façon rudimentaire) un contenu HTML en Markdown.
    Pour quelque chose de plus élaboré, on peut envisager l'utilisation
    de bibliothèques comme html2text, ou l’écriture de règles plus fines.
    """
    text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n', html_content, flags=re.DOTALL)
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n', text, flags=re.DOTALL)

    text = re.sub(r'<h3 class="code-header"[^>]*>(.*?)</h3>', r'`\1`\n', text, flags=re.DOTALL)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<a class="doc-anchor" [^>]*>(.*?)</a>', r'', text, flags=re.DOTALL)
    text = re.sub(r'<a[^>]*class="anchor"[^>]*>(.*?)</a>', r'', text, flags=re.DOTALL)
    text = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1\n`', text, flags=re.DOTALL)
    text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', text, flags=re.DOTALL)
    text = re.sub(r'\&lt;', r' <', text, flags=re.DOTALL)
    # Supprimer toutes les balises HTML restantes
    text = re.sub(r'<[^>]+>', '', text)
    # Retirer les espaces multiples
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = text.strip()
    return text


def get_soup(url):
    r = requests.get(url)
    r.raise_for_status()
    return BeautifulSoup(r.text, 'html.parser')

def extract_main_content(soup):
    main_div = soup.find(id="main-content")

    for nav_tag in main_div.find_all(["nav", "aside", "rustdoc-search", "copy-path", "rustdoc-toolbar", "button", "script", "rustdoc-breadcrumbs"]):
        nav_tag.decompose()

    disclaimers = main_div.find_all(class_="sub-heading")
    for d in disclaimers:
        d.decompose()

    return str(main_div)


def parse_links_struct(links_struct, dict_links, src):
    list_links = []
    for struc in links_struct:
        key = src + struc['href']
        if key not in dict_links:
            dict_links[key] = False
            list_links.append(key)
    return list_links




def get_doc_links(soup, dict_links, src):
    doc_links = list()

    sidebar = soup.find_all("div", class_="item-name")
    if sidebar:
        for s in sidebar:
            a = s.next_element.attrs
            doc_links.append(a)
            href = a["href"]
            print(href)

    print(doc_links)
    return parse_links_struct(doc_links, dict_links, src)
    # Exemples de selecteurs possibles.
    # On pourrait aussi parcourir toutes les balises <a> et filtrer.

    # sidebar = soup.find("section", class_="content")
    # if sidebar:
    #     for a in sidebar.find_all("a", href=True):
    #         href = a["href"]
    #         if href.startswith("./") or href.startswith("../"):
    #             doc_links.add(href)
    #         elif href.startswith("#"):
    #             print(href)
    # print(doc_links)
    #
    # # Conversion en liens absolus
    # absolute_links = []
    # for link in doc_links:
    #     if link.startswith("./"):
    #         absolute_links.append(CRATE_URL + link[2:])  # retire "./" et ajoute base
    #     elif link.startswith("../"):
    #         # remontée d'un niveau : on retire '../' et on concatène
    #         # Cependant, il peut y avoir plusieurs niveaux. À ajuster si besoin.
    #         # Ex : "../foo" => ndarray/foo
    #         link_part = link.lstrip("./")
    #         absolute_links.append(os.path.join(CRATE_URL, link_part))
    #     else:
    #         # Autres cas, potentiellement des liens complets
    #         if link.startswith("http"):
    #             absolute_links.append(link)
    #         else:
    #             absolute_links.append(CRATE_URL + link)

    #return list(set(doc_links))

def scrape_page(link: str, visited: dict):
    page_soup = get_soup(link)

    page_content_html = extract_main_content(page_soup)
    main_content_md = to_markdown(page_content_html)


    links = []
    if link.endswith("index.html"):
        link_no_index = link.rsplit("/", 1)[0] + "/"
        links = get_doc_links(page_soup, visited, link_no_index)


    doc_md = main_content_md
    for link in links:
        if not visited[link]:
            visited[link] = True
            try:
                doc_md += f"\n## Page : {link}\n\n"
                doc_md += scrape_page(link, visited)

            except Exception as e:
                print(f"Impossible de scraper {link} : {e}")
    return doc_md

def scrape_ndarray_docs():
    # 1. Récupérer la page d'accueil
    main_soup = get_soup(CRATE_URL)

    # 2. Récupérer le contenu principal
    main_content_html = extract_main_content(main_soup)


    # 3. Conversion en Markdown
    main_content_md = to_markdown(main_content_html)

    # 4. Récupérer la liste des liens internes
    links = get_doc_links(main_soup)
    print(links)

    all_docs_md = main_content_md + "\n\n"

    visited = set()  # pour éviter de scraper plusieurs fois la même page
    for link in links:
        if link not in visited:
            visited.add(link)
            try:
                page_soup = get_soup(link)
                page_content_html = extract_main_content(page_soup)
                page_content_md = to_markdown(page_content_html)

                all_docs_md += f"## Page : {link}\n\n"
                all_docs_md += page_content_md + "\n\n"

            except Exception as e:
                print(f"Impossible de scraper {link} : {e}")

    # 6. Sauvegarder le tout dans un fichier Markdown
    with open("ndarray_doc.md", "w", encoding="utf-8") as f:
        f.write(all_docs_md)


if __name__ == "__main__":
    #scrape_ndarray_docs()
    visited = {}
    global_md = scrape_page(CRATE_URL, visited)
    with open("doc.md", "w", encoding="utf-8") as f:
        f.write(global_md)
#%%
