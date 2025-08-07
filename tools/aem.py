import requests
import json
import re
import html
from dateutil import parser
from datetime import datetime, timezone

# 1. Configurações
author_url = "https://author-p120717-e1174076.adobeaemcloud.com"
public_url_base = "https://portal.maplebear.com.br"
query_path = "/bin/querybuilder.json"
credentials = ("turing_user", "5DIzbK4@")

def isEvent(path):
    return '/content/dam/maple-bear/events' in path

def isPost(path):
    return '/content/maple-bear/posts' in path

def getPathByName(name, type = 'posts'):
    return f"{public_url_base}/{type}/{name}"

def integrationStatus(allPostsTuring, contentFragment):
    for postTuring in allPostsTuring:
        if contentFragment['path'] == postTuring['id']:
            dateTuring = parser.isoparse(postTuring['publication_date'])
            dateSpPost = datetime.fromtimestamp(contentFragment["lastModified"] / 1000, tz=timezone.utc)

            if dateTuring < dateSpPost:
                return {"status": 1, "id": contentFragment['path']}
            else:
                return {"status": 3, "id": contentFragment['path']}

    return {"status": 1, "id": None}

def getOriginProprieties(id, params):
    url = author_url + id + '.json'
    response = requests.get(url, params=params, auth=credentials)

    if response.status_code != 200:
        print("Erro ao consultar Content Proprieties:", response.status_code, url)
        return False

    return response.json()

def getPageContent(id):
    siteName = id.replace('/content/dam/maple-bear/posts/', '')
    page_url = f"{public_url_base}/{siteName}.model.json"

    try:
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
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
                        text = value["text"] or ""
                        results.append('<span>' + remove_html_tags_and_special_chars(text) + '</span>')

            # Verifica se existe "accordionItems"
            if "accordionItems" in obj:
                for accordion in obj["accordionItems"]:
                    title = accordion.get("accordionTitle") or ""
                    paragraph = remove_html_tags_and_special_chars(accordion.get("paragraph") or "")
                    results.append(f'<span>{title}: {paragraph}</span>')

            # Verifica se existe "tabsItems"
            if "tabsItems" in obj:
                for tabs in obj["tabsItems"]:
                    title = tabs.get("tabsItemTitle") or ""
                    text = remove_html_tags_and_special_chars(tabs.get("tabsItemText") or "")
                    results.append(f'<span>{title}: {text}</span>')

            # Continua percorrendo os filhos
            for value in obj.values():
                recursive_search(value)

        elif isinstance(obj, list):
            for item in obj:
                recursive_search(item)

    recursive_search(data)
    return results

def getContentFragmentProprieties(id, params):
    url = author_url + id.replace('content/maple-bear/posts', 'content/dam/maple-bear/posts') + '/jcr:content/data/master.json'
    response = requests.get(url, params=params, auth=credentials)

    if response.status_code != 200:
        print("Erro ao consultar Content Proprieties:", response.status_code, url)
        return False

    return response.json()

def getAllContentFragment(params):
    response = requests.get(author_url + query_path, params=params, auth=credentials)

    if response.status_code != 200:
        print("Erro ao consultar Content Fragment:", response.status_code, response.text)
        exit()

    data = response.json()
    return data.get("hits", [])

def remove_html_tags_and_special_chars(text):
    # Converte entidades HTML (&nbsp;, etc.)
    if text:
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
    else:
        return ''
