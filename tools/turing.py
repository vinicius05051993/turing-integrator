import requests
from datetime import datetime, timezone
from dateutil import parser
import re
from html import unescape
import json
import os
import base64

GITHUB_API = "https://api.github.com"
REPO = "vinicius05051993/turing-integrator"
BRANCH = "main"
PASTA = "blob"
GITHUB_TOKEN = os.environ.get("API_TOKEN")

TURING_HOMOLOG = {
    'host': 'buscahml.maplebear.com.br',
    'url_import': 'https://buscahml.maplebear.com.br/api/sn/import',
    'key': 'd2e922bb73854fb3bcd04bc87',
    'locale': 'pt_BR',
    'site': 'maplebear-stage-publish',
    'auth': 'https://2746bef7-54d2-4f0c-9fab-43175e1880ab.prod2-care.sprinklr.com/community/api/v1/auth/social?communityId=2746bef7-54d2-4f0c-9fab-43175e1880ab&provider=MAPLE_BEAR&returnTo=###'
}

TURING_PRODUCTION = {
    'host': 'busca.maplebear.com.br',
    'url_import': 'https://busca.maplebear.com.br/api/sn/import',
    'key': '2803004d34004b4e8e8cb709f',
    'locale': 'pt_BR',
    'site': 'maplebear-prd-publish',
    'auth': 'https://2746bef7-54d2-4f0c-9fab-43175e1880ab.prod2-care.sprinklr.com/community/api/v1/auth/social?communityId=2746bef7-54d2-4f0c-9fab-43175e1880ab&provider=MAPLE_BEAR&returnTo=###'
}

DATA_IN_USE = TURING_PRODUCTION

def getAllTuring(page, type = 'all'):
    try:
#       https://buscahml.maplebear.com.br/api/sn/maplebear-stage-publish/search?p=1&rows=600&_setlocale=pt_BR&nfpr=0&q=*
        if type == 'all':
            resposta = requests.get('https://'+ DATA_IN_USE['host'] +'/api/sn/'+ DATA_IN_USE['site'] +'/search?p='+ str(page) +'&rows=200&_setlocale='+ DATA_IN_USE['locale'] +'&nfpr=0&q=*', verify=False)
        else:
            resposta = requests.get('https://'+ DATA_IN_USE['host'] +'/api/sn/'+ DATA_IN_USE['site'] +'/search?p='+ str(page) +'&rows=200&_setlocale='+ DATA_IN_USE['locale'] +'&nfpr=0&q=*&fq[]=mbtype:' + type, verify=False)

        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException as e:
        print('Erro ao buscar dados:', e)
        return None

def getAllTuringIds(type='all'):
    ids = []
    for page in range(1, 100):
        datas = getAllTuring(page, type)
        queryContext = datas.get("queryContext", {})

        if (page > queryContext['pageCount']):
            break

        document = datas.get("results", {}).get("document", [])
        for doc in document:
            if type == 'all' or type == doc.get("fields", {}).get("mbtype", False):
                ids.append({'id': doc['fields']['id'], 'publication_date': doc['fields']['publication_date']})

    return ids

def integrationStatus(turingDatas, spPost):
    for index, turingData in enumerate(turingDatas):
        if turingData['id'] == spPost['id']:
            dateTuring = parser.isoparse(turingData['publication_date'])
            dateSpPost = datetime.fromtimestamp(spPost["lastActivityAt"] / 1000, tz=timezone.utc)

            if spPost['id'] == '66c79943dac62338bfc7d25d':
                print(spPost)

            if dateTuring < dateSpPost:
                return {"status": 3, "id": turingData["id"], "key": index}
            else:
                return {"status": 3, "id": turingData["id"], "key": index}

    return {"status": 1, "id": None, "key": None}

def send(spPost):
    headers = {
        'Key': DATA_IN_USE['key'],
        'Content-Type': 'application/json',
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }

    dateUpdate = datetime.fromtimestamp(spPost["lastActivityAt"] / 1000, tz=timezone.utc).isoformat()

    if len(spPost['m']) < 0:
        html = get_text_with_images(spPost['m'])
    else:
        html = get_only_texts(spPost['m'])

    data = {
        'turingDocuments': [
            {
                'turSNJobAction': 'CREATE',
                'locale': DATA_IN_USE['locale'],
                'siteNames': [DATA_IN_USE['site']],
                'attributes': {
                    'id': spPost['id'],
                    'title': spPost['t'],
                    'abstract': ' - '.join(spPost['tagLabels']) + "\n " + get_only_texts(spPost['m'])[:12000],
                    'html': html,
                    'url': getUrlWithAuth(spPost['path']),
                    'mbtype': 'manual',
                    'area': get_tags(spPost['categoryIds'], 'area'),
                    'theme': get_tags(spPost['categoryIds'], 'theme'),
#                     'area_name': get_tags_name(spPost['categoryIds'], 'area'),
#                     'theme_name': get_tags_name(spPost['categoryIds'], 'theme'),
                    'functiontags': get_tags(spPost['categoryIds'], 'function'),
                    'otherTags': [],
                    'notify': False,
                    'content_tags': spPost['tagLabels'],
                    'publication_date': dateUpdate,
                    'modification_date': dateUpdate,
                    'openInNewTab': True
                }
            }
        ]
    }

    response = requests.post(DATA_IN_USE['url_import'], json=data, headers=headers, verify=False)
    response.raise_for_status()
    print('Publicação enviada com sucesso:', response.status_code, response.text, response.json(), json.dumps(data))

def delete(id):
    headers = {
        'Key': DATA_IN_USE['key'],
        'Content-Type': 'application/json',
        'Cookie': 'XSRF-TOKEN=7b04df8b-ac27-4e84-b1f2-ed227537aa5d'
    }

    data = {
        'turingDocuments': [
            {
                'turSNJobAction': 'DELETE',
                'attributes': {'id': id},
                'locale': DATA_IN_USE['locale'],
                'siteNames': [DATA_IN_USE['site']]
            }
        ]
    }

    response = requests.post(DATA_IN_USE['url_import'], json=data, headers=headers, verify=False)
    response.raise_for_status()
    print('Publicação deletada com sucesso:', response.status_code, json.dumps(data))

def getUrlWithAuth(url):
    url = "https://conhecimento-maplebear.sprinklr.com/articles/" + url
    return DATA_IN_USE['auth'].replace("###", url)

def get_only_texts(html: str) -> str:
    text_captured = ''
    matches = re.findall(r'<(?:span|p)[^>]*>(.*?)</(?:span|p)>', html, flags=re.IGNORECASE | re.DOTALL)

    if matches:
        text_captured = ' '.join(matches)

    text_captured = re.sub(r'<[^>]*>', '', text_captured)  # Remove any remaining tags
    text_captured = re.sub(r'[^\w\s\?]', '', text_captured)  # Remove non-alphanumeric chars, except ?

    return text_captured.strip()

def upload_image_to_github(image_bytes, filename):
    url = f"{GITHUB_API}/repos/{REPO}/contents/{PASTA}/{filename}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "message": f"Adicionando imagem {filename}",
        "branch": BRANCH,
        "content": base64.b64encode(image_bytes).decode("utf-8")
    }

    response = requests.put(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{PASTA}/{filename}"
    else:
        raise Exception(f"Erro ao enviar {filename}: {response.text}")

def get_text_with_images(html: str) -> str:
    image_links = {}
    contador = 0

    def substituir_img(match):
        nonlocal contador
        src = match.group(1)
        try:
            img_response = requests.get(src)
            img_response.raise_for_status()
            extension = src.split('.')[-1].split('?')[0].lower()
            filename = f"img_{contador}.{extension}"
            github_url = upload_image_to_github(img_response.content, filename)
            marcador = f"[{github_url}]"
            image_links[f"__IMG{contador}__"] = marcador
        except Exception as e:
            print(f"Erro ao processar imagem {src}: {e}")
            image_links[f"__IMG{contador}__"] = "[imagem inválida]"
        marcador_simples = f"__IMG{contador}__"
        contador += 1
        return marcador_simples

    html_com_marcadores = re.sub(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', substituir_img, html, flags=re.IGNORECASE)
    matches = re.findall(r'<(span|p)[^>]*>(.*?)<\/\1>', html_com_marcadores, flags=re.IGNORECASE | re.DOTALL)
    textos_capturados = ' '.join([unescape(m[1]) for m in matches])
    texto_limpo = re.sub(r'[^\w\s\[\]_\?]', '', re.sub(r'<[^>]+>', '', textos_capturados), flags=re.UNICODE)

    for marcador, link in image_links.items():
        texto_limpo = texto_limpo.replace(marcador, link)

    return texto_limpo

def get_tags_name(category_ids: list, tag_type: str) -> list:
    if tag_type == 'area':
        tag_relation = {
            '673ef6a1ec0d3452790927a2': "Acadêmico",
            "673ef6a7ec0d345279092ce0": "Administrativo e Financeiro",
            "673ef6aeec0d34527909328a": "Marketing",
            "6740b0b4ec0d345279f6f31e": "Comercial e Vendas",
            "67e1673057c3b02ea30b4cc5": "Gente",
            "67e1679557c3b02ea30c415a": "Área Gestão Escolar",
            "6740b144ec0d345279f7e8ba": "Área Tecnologia",
            "6740b12bec0d345279f7b432": "Área Liderança"
        }
    elif tag_type == 'theme':
        tag_relation = {
            '67583dbae71a454adb45b281': "Estudos de Mercado",
            '67583ff2e71a454adb4a511a': "Novidades Tecnológicas",
            '67584002e71a454adb4a7626': "Treinamentos",
            '6758401ce71a454adb4aad04': "Enxoval de Peças",
            '67584556e71a454adb55c843': "Ações Parcerias",
            '67584560e71a454adb55e0bf': "Suporte",
            '67584577e71a454adb560f2a': "Treinamentos e Eventos",
            '6758458de71a454adb563f81': "Arquitetura e Expansão",
            '6758459fe71a454adb5665a6': "Projetos Escolares",
            '675845aee71a454adb5684d1': "Programas Maple Bear",
            '675845c7e71a454adb56bc39': "Ecossistema Maple Bear",
            '675845d5e71a454adb56da17': "Comunicação",
            '675845eae71a454adb570a17': "Matrícula Rematrícula",
            '675845f9e71a454adb5727ca': "Gestão Escolar"
        }
    elif tag_type == 'function':
        tag_relation = {
            "673507438bc4a21efe2310ca": "Owner"
        }
    else:
        return []

    return [tag_relation[cat_id] for cat_id in category_ids if cat_id in tag_relation]

def get_tags(category_ids: list, tag_type: str) -> list:
    if tag_type == 'area':
        tag_relation = {
            '673ef6a1ec0d3452790927a2': "maple-bear:area/academico",
            "673ef6a7ec0d345279092ce0": "maple-bear:area/administrativo-financeiro",
            "673ef6aeec0d34527909328a": "maple-bear:area/marketing",
            "6740b0b4ec0d345279f6f31e": "maple-bear:area/comercial-vendas",
            "67e1673057c3b02ea30b4cc5": "maple-bear:area/gente",
            "67e1679557c3b02ea30c415a": "maple-bear:area/gestaoescolar",
            "6740b144ec0d345279f7e8ba": "maple-bear:area/tecnologia",
            "6740b12bec0d345279f7b432": "maple-bear:area/lideranca"
        }
    elif tag_type == 'theme':
        tag_relation = {
            '67583dbae71a454adb45b281': "maple-bear:theme/estudos-de-mercado",
            '67583ff2e71a454adb4a511a': "maple-bear:theme/edtech-sistemas",
            '67584002e71a454adb4a7626': "maple-bear:theme/treinamentos",
            '6758401ce71a454adb4aad04': "maple-bear:theme/enxoval-de-peças",
            '67584556e71a454adb55c843': "maple-bear:theme/acoes-parcerias",
            '67584560e71a454adb55e0bf': "maple-bear:theme/suporte",
            '67584577e71a454adb560f2a': "maple-bear:theme/treinamentos-&-eventos",
            '6758458de71a454adb563f81': "maple-bear:theme/arquitetura-expansao",
            '6758459fe71a454adb5665a6': "maple-bear:theme/projetos-escolares",
            '675845aee71a454adb5684d1': "maple-bear:theme/programas-maple-bear",
            '675845c7e71a454adb56bc39': "maple-bear:theme/ecossistema-maple-bear",
            '675845d5e71a454adb56da17': "maple-bear:theme/comunica--o",
            '675845eae71a454adb570a17': "maple-bear:theme/matricula-rematricula",
            '675845f9e71a454adb5727ca': "maple-bear:theme/gestao-escolar"
        }
    elif tag_type == 'function':
        tag_relation = {
            "673507438bc4a21efe2310ca": "maple-bear:function/owner"
        }
    else:
        return []

    return [tag_relation[cat_id] for cat_id in category_ids if cat_id in tag_relation]