import requests
import re

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

def getPageOfPost(hit):
    siteName = hit.get("name", "")
    page_url = f"{public_url_base}/posts/{siteName}.model.json"

    try:
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
        return response.text.json()
    except Exception as e:
        print(f"❌ Erro ao acessar {page_url}: {e}")
        return False

def find_all_objects(data):
    results = []

    def recursive_search(obj):
        if isinstance(obj, dict):
            if "accordionItems" in obj:
                for accordion in obj['accordionItems']:
                    results.append(accordion['accordionTitle'] + ' ' + accordion['paragraph'])
            for value in obj.values():
                recursive_search(value)
        elif isinstance(obj, list):
            for item in obj:
                recursive_search(item)

    recursive_search(data)
    return results


def getAllPosts():
    response = requests.get(author_url + query_path, params=params, auth=credentials)

    if response.status_code != 200:
        print("Erro ao consultar páginas:", response.status_code, response.text)
        exit()

    data = response.json()
    return data.get("hits", [])

def get_only_texts(html: str) -> str:
    text_captured = ''
    matches = re.findall(r'<(?:span|p)[^>]*>(.*?)</(?:span|p)>', html, flags=re.IGNORECASE | re.DOTALL)

    if matches:
        text_captured = ' '.join(matches)

    text_captured = re.sub(r'<[^>]*>', '', text_captured)  # Remove any remaining tags
    text_captured = re.sub(r'[^\w\s\?]', '', text_captured)  # Remove non-alphanumeric chars, except ?

    return text_captured.strip()

