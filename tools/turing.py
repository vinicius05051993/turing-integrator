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
    for turingData in turingDatas:
        if turingData['id'] == spPost['id']:
            dateTuring = parser.isoparse(turingData['publication_date'])
            dateSpPost = datetime.fromtimestamp(spPost["lastActivityAt"] / 1000, tz=timezone.utc)

            if dateTuring < dateSpPost:
                return {"status": 1, "id": turingData["id"]}
            else:
                return {"status": 3, "id": turingData["id"]}

    return {"status": 1, "id": None}

def send(spPost, mbtype = 'manual'):
    headers = {
        'Key': DATA_IN_USE['key'],
        'Content-Type': 'application/json',
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }

    dateUpdate = datetime.fromtimestamp(spPost["lastActivityAt"] / 1000, tz=timezone.utc).isoformat()

    turingFields = {
       'id': spPost['id'],
       'title': spPost['t'],
       'abstract': ' - '.join(spPost['tagLabels']),
       'text': get_text_with_images_and_pdf(spPost['m'], spPost['id']),
       'url': spPost.get('pathFragment') or getUrlWithAuth(spPost['path']),
       'mbtype': mbtype,
       'area': spPost.get('tagFragmentArea') or get_tags(spPost['categoryIds'], 'area'),
       'theme': spPost.get('tagFragmentTheme') or get_tags(spPost['categoryIds'], 'theme'),
#                     'area_name': get_tags_name(spPost['categoryIds'], 'area'),
#                     'theme_name': get_tags_name(spPost['categoryIds'], 'theme'),
       'functiontags': get_tags(spPost['categoryIds'], 'function'),
       'otherTags': [],
       'notify': False,
       'content_tags': spPost['tagLabels'][:2],
       'publication_date': dateUpdate,
       'modification_date': dateUpdate,
       'openInNewTab': True,
       'image': spPost.get('image', ''),
       'highlights': spPost.get('highlights', False)
   }

    data = {
        'turingDocuments': [
            {
                'turSNJobAction': 'CREATE',
                'locale': DATA_IN_USE['locale'],
                'siteNames': [DATA_IN_USE['site']],
                'attributes': turingFields
            }
        ]
    }

    response = requests.post(DATA_IN_USE['url_import'], json=data, headers=headers, verify=False)
    response.raise_for_status()
    print('Publicação enviada com sucesso:', response.status_code, response.text, response.json(), json.dumps(data))

    return turingFields

def delete(id, remove_images = False):
    headers = {
        'Key': DATA_IN_USE['key'],
        'Content-Type': 'application/json',
        'Cookie': 'XSRF-TOKEN=7b04df8b-ac27-4e84-b1f2-ed227537aa5d'
    }

    if remove_images:
        remover_arquivos_do_github_por_id(id)

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

def remover_arquivos_do_github_por_id(id):
    url_tree = f"{GITHUB_API}/repos/{REPO}/git/trees/{BRANCH}?recursive=1"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    resposta = requests.get(url_tree, headers=headers)
    if resposta.status_code != 200:
        print(f"Erro ao listar arquivos: {resposta.text}")
        return

    arquivos = resposta.json().get("tree", [])
    for arquivo in arquivos:
        path = arquivo["path"]
        if path.startswith(f"{PASTA}/{id}_"):  # Ex: blob/123_abc.png
            filename = path.split("/")[-1]
            url_delete = f"{GITHUB_API}/repos/{REPO}/contents/{path}"

            get_res = requests.get(url_delete, headers=headers)
            if get_res.status_code != 200:
                print(f"Erro ao obter SHA de {path}: {get_res.text}")
                continue

            sha = get_res.json().get("sha")

            delete_payload = {
                "message": f"Remover arquivo {filename}",
                "sha": sha,
                "branch": BRANCH
            }
            delete_res = requests.delete(url_delete, headers=headers, json=delete_payload)
            if delete_res.status_code == 200:
                print(f"Arquivo {filename} removido com sucesso.")
            else:
                print(f"Erro ao remover {filename}: {delete_res.text}")

def upload_file_to_github(file_bytes, filename, tipo="arquivo"):
    url = f"{GITHUB_API}/repos/{REPO}/contents/{PASTA}/{filename}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "message": f"Adicionando {tipo} {filename}",
        "branch": BRANCH,
        "content": base64.b64encode(file_bytes).decode("utf-8")
    }

    response = requests.put(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{PASTA}/{filename}"
    else:
        raise Exception(f"Erro ao enviar {filename}: {response.text}")

def get_text_with_images_and_pdf(html: str, id) -> str:
    links_substituidos = {}
    contador = 0

    remover_arquivos_do_github_por_id(id)

    def substituir_img(match):
        nonlocal contador
        src = unescape(match.group(1))
        marcador = f"__ARQ{contador}__"
        try:
            response = requests.get(src)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if "image" not in content_type:
                raise Exception("Conteúdo não é imagem")

            extension = src.split('.')[-1].split('?')[0].lower()
            if not extension or len(extension) > 5:
                extension = content_type.split('/')[-1] or "png"

            filename = f"{id}_{contador}.{extension}"
            github_url = upload_file_to_github(response.content, filename, tipo="imagem")
            links_substituidos[marcador] = f"[{github_url}]"
        except Exception as e:
            print(f"Erro ao processar imagem {src}: {e}")
            links_substituidos[marcador] = "[" + src + "]"
        contador += 1
        return marcador

    def substituir_pdf(match):
        nonlocal contador
        href = unescape(match.group(1))
        marcador = f"__ARQ{contador}__"
        try:
            response = requests.get(href)
            response.raise_for_status()
            if "application/pdf" not in response.headers.get("Content-Type", ""):
                raise Exception("Conteúdo não é PDF")

            filename = f"{id}_{contador}.pdf"
            github_url = upload_file_to_github(response.content, filename, tipo="PDF")
            links_substituidos[marcador] = f"[{github_url}]"
        except Exception as e:
            print(f"Erro ao processar PDF {href}: {e}")
            links_substituidos[marcador] = "[" + href + "]"
        contador += 1
        return marcador

    def substituir_link(match):
        nonlocal contador
        href = unescape(match.group(1))
        if href.lower().endswith('.pdf'):
            return match.group(0)  # Ignora, já tratado no bloco PDF
        marcador = f"__ARQ{contador}__"
        links_substituidos[marcador] = f"[{href}]"
        contador += 1
        return marcador

    # Substitui imagens
    html = re.sub(
        r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
        substituir_img,
        html,
        flags=re.IGNORECASE
    )

    # Substitui PDFs
    html = re.sub(
        r'<a[^>]+href=["\']([^"\']+\.pdf(\?[^"\']*)?)["\'][^>]*>.*?</a>',
        substituir_pdf,
        html,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Substitui links genéricos (não PDF)
    html = re.sub(
        r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>.*?</a>',
        substituir_link,
        html,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Extrai e limpa texto
    matches = re.findall(
        r'<(span|p|div|a)[^>]*>(.*?)</\1>',
        html,
        flags=re.IGNORECASE | re.DOTALL
    )
    textos_capturados = ' '.join([unescape(m[1]) for m in matches])
    texto_limpo = re.sub(r'<[^>]+>', '', textos_capturados)
    texto_limpo = re.sub(r'[^\w\s\[\]_\-.:/?]', '', texto_limpo, flags=re.UNICODE)

    for marcador, link in links_substituidos.items():
        texto_limpo = texto_limpo.replace(marcador, link)

    texto_limpo = texto_limpo.replace('\n', '')
    texto_limpo = ' '.join(texto_limpo.split())
    texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()
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