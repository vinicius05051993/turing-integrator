import requests
import json
import re
import html

# 1. Configurações
author_url = "https://author-p120717-e1174076.adobeaemcloud.com"
public_url_base = "https://portal.maplebear.com.br"
query_path = "/bin/querybuilder.json"
credentials = ("turing_user", "5DIzbK4@")

params = {
    "path": "/content/maple-bear/posts",
    "type": "cq:Page",
    "property": "jcr:content/cq:lastReplicationAction",
    "property.value": "Activate",
    "p.limit": "-1",
    "orderby": "path"
}

def getPageOfPost(id):
    siteName = id.replace('/content/dam/maple-bear/posts/', '')
    page_url = f"{public_url_base}/posts/{siteName}.model.json"

    try:
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
        print(response.text)
        return json.loads(response.text)
    except Exception as e:
        print(f"❌ Erro ao acessar {page_url}: {e}")
        return False

def find_all_objects(data):
    results = []

    def recursive_search(obj):
        if isinstance(obj, dict):
            # Verifica se existe alguma chave que começa com "richtext"
            for key, value in obj.items():
                if key.startswith("richtext"):
                    if isinstance(value, dict) and "text" in value:
                        results.append(remove_html_tags_and_special_chars(value["text"]))

            # Verifica se existe "accordionItems"
            if "accordionItems" in obj:
                for accordion in obj["accordionItems"]:
                    results.append(
                        accordion.get("accordionTitle", "") + ": " +
                        remove_html_tags_and_special_chars(accordion.get("paragraph", ""))
                    )

            if "tabsItems" in obj:
                for tabs in obj["tabsItems"]:
                    results.append(
                        tabs.get("tabsItemTitle", "") + ": " +
                        remove_html_tags_and_special_chars(tabs.get("tabsItemText", ""))
                    )

            # Continua percorrendo os filhos
            for value in obj.values():
                recursive_search(value)

        elif isinstance(obj, list):
            for item in obj:
                recursive_search(item)

    recursive_search(data)
    return results

# def getAllPosts():
#     response = requests.get(author_url + query_path, params=params, auth=credentials)
#
#     if response.status_code != 200:
#         print("Erro ao consultar páginas:", response.status_code, response.text)
#         exit()
#
#     data = response.json()
#     return data.get("hits", [])

def remove_html_tags_and_special_chars(text):
    # Converte entidades HTML (&nbsp;, etc.)
    text = html.unescape(text)

    # Remove espaços não separáveis (incluindo \xa0)
    text = text.replace('\xa0', ' ')

    # Converte <a href="...">texto</a> para: texto [link]
    text = re.sub(r'<a [^>]*href=["\'](.*?)["\'][^>]*>(.*?)</a>', r'\2 [\1]', text, flags=re.IGNORECASE)

    # Remove todas as outras tags HTML
    text = re.sub(r'<[^>]+>', '', text)

    # Remove emojis comuns (como 📷, 😃)
    text = re.sub(r'[\U0001F300-\U0001FAFF\u2600-\u26FF\u2700-\u27BF]+', '', text)

    # Remove \r \n \t e espaços múltiplos
    text = re.sub(r'[\r\n\t]', '', text)
    text = re.sub(r' +', ' ', text)

    return text.strip()

