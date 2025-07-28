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

def getHtmlOfPost(hit):
    path = hit.get("path", "")
    if not path.startswith("/content/maple-bear/posts"):
        return false

    relative_path = path.replace("/content/maple-bear", "")
    if relative_path.endswith("/jcr:content"):
        relative_path = relative_path.replace("/jcr:content", "")

    page_url = f"{public_url_base}{relative_path}"

    try:
        html_response = requests.get(page_url, timeout=10)
        return html_response.text
    except Exception as e:
        print(f"❌ Erro ao acessar {page_url}: {e}")

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

