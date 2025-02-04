import re

import requests
from bs4 import BeautifulSoup
from src.config import RAG_FILE, DOCUMENTS_DIR

BASE_URL = "https://docs.rs"
CRATE_URL = "https://docs.rs/burn/latest/burn/index.html"




def to_markdown(html_content):
    text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n', html_content, flags=re.DOTALL)
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n', text, flags=re.DOTALL)

    text = re.sub(r'<h3 class="code-header"[^>]*>(.*?)</h3>', r'`\1`\n', text, flags=re.DOTALL)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<h4[^>]*>(.*?)</h4>', r'### \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<a class="doc-anchor" [^>]*>(.*?)</a>', r'', text, flags=re.DOTALL)
    text = re.sub(r'<a[^>]*class="anchor"[^>]*>(.*?)</a>', r'', text, flags=re.DOTALL)
    text = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1\n`', text, flags=re.DOTALL)
    text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', text, flags=re.DOTALL)
    text = re.sub(r'<section[^>]*>(.*?)</section>', r'\1\n', text, flags=re.DOTALL)
    text = re.sub(r'\&lt;', r' <', text, flags=re.DOTALL)
    text = re.sub(r'\&gt;', r'> ', text, flags=re.DOTALL)
    # Supprimer toutes les balises HTML restantes
    #text = re.sub(r'<[^>]+>', '', text)

    text = re.sub(r'<h5[^>]*>(.*?)</h5>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<details[^>]*>(.*?)</details>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<div[^>]*>(.*?)</div>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<ul[^>]*>(.*?)</ul>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<pre[^>]*>(.*?)</pre>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<wbr/>', r'', text, flags=re.DOTALL)

    text = re.sub(r'<summary class="hideme"[^>]*>(.*?)</summary>', r'', text, flags=re.DOTALL)
    text = re.sub(r'<summary[^>]*>(.*?)</summary>', r'\1', text, flags=re.DOTALL)
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

    for nav_tag in main_div.find_all(
            ["nav", "aside", "rustdoc-search", "copy-path", "rustdoc-toolbar", "button", "script",
             "rustdoc-breadcrumbs"]):
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


def scrape_page(link: str, visited: dict):
    page_soup = get_soup(link)

    title = link.split("/")[-1][:-5]
    if title == "index":
        title = link.split("/")[-2]

    title = title + ".md"

    print(title)


    page_content_html = extract_main_content(page_soup)
    main_content_md = to_markdown(page_content_html)

    with open(DOCUMENTS_DIR / title, "w", encoding="utf-8") as f:
        f.write(main_content_md)

    links = []
    if link.endswith("index.html"):
        link_no_index = link.rsplit("/", 1)[0] + "/"
        links = get_doc_links(page_soup, visited, link_no_index)

    for link in links:
        if not visited[link]:
            visited[link] = True
            try:
                 scrape_page(link, visited)

            except Exception as e:
                print(f"Impossible de scraper {link} : {e}")


def main(link):
    visited = dict()
    scrape_page(link, visited)

if __name__ == "__main__":
    main(CRATE_URL)

# %%
