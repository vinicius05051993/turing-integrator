import requests
from dateutil import parser
import re

CHATVOLT_API_URL = 'https://api.chatvolt.ai/'
DATASTORE_ID = 'cmbauo40600brx87n8gazln1j'

HEADERS_DESTINO = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 3f157bd4-64ae-4ecb-ac8d-ffe0f89b2149'
}

def send(docFields : dict):
    match docFields.get('mbtype', false):
        case 'post':
            sendPost(docFields)
        case 'event':
            sendEvent(docFields)
        case 'manual':
            if "FAQ" in docFields.get('content_tags', []):
                sendFAQ(docFields)
            else:
                sendManual(docFields)

def sendPost(docFields : dict):
    return false
    try:
        payload = {
           "name": getIdName(docFields),
           "datastoreId": DATASTORE_ID,
           "datasourceText": "[post] " + docFields.get('text', ''),
           "type": "file",
           "config": {
               "tags": docFields.get('content_tags', []),
               "source_url": docFields.get('url', ''),
               "mime_type": "text/plain"
           }
        }

        resposta = requests.post(CHATVOLT_API_URL + "datasources", json=payload, headers=HEADERS_DESTINO)
        resposta.raise_for_status()
        print('Publicação enviada com sucesso:', resposta.status_code)
    except requests.RequestException as e:
        print('Erro ao enviar publicação:', e)

def sendEvent(docFields : dict):
    return false
    try:
        dataSourcetext = ""
        if docFields.get("allDay", False):
            dataSourcetext += "Evento dia todo. "
        else:
            dataSourcetext += "Evento não é dia todo. "

        dataSourcetext += "Data inicial: " + docFields.get("initialDate", "") + ". "
        dataSourcetext += "Data final: " + docFields.get("finishDate", "") + ". "

        payload = {
           "name": getIdName(docFields),
           "datastoreId": DATASTORE_ID,
           "datasourceText": "[event] " + dataSourcetext,
           "type": "file",
           "config": {
               "tags": docFields.get('content_tags', []),
               "source_url": docFields.get('url', ''),
               "mime_type": "text/plain"
           }
        }

        resposta = requests.post(CHATVOLT_API_URL + "datasources", json=payload, headers=HEADERS_DESTINO)
        resposta.raise_for_status()
        print('Evento enviado com sucesso:', resposta.status_code)
    except requests.RequestException as e:
        print('Erro ao enviar eventos:', e)

def sendFAQ(docFields : dict):
    try:
        question, response = separar_perguntas_respostas(docFields['html'].replace('Perguntas ', ''))
        payload = {
           "name": getIdName(docFields),
           "datastoreId": DATASTORE_ID,
           "datasourceText": "[faq] " + response,
           "type": "qa",
           "isUpdateText": True,
           "config": {
               "tags": docFields.get('content_tags', []),
               "source_url": docFields.get('url', ''),
               "question": question,
               "answer": response
           }
        }

        resposta = requests.post(CHATVOLT_API_URL + "datasources", json=payload, headers=HEADERS_DESTINO)
        resposta.raise_for_status()
        print('FAQ enviado com sucesso:', resposta.status_code)
    except requests.RequestException as e:
        print('Erro ao enviar manual:', e)

def sendManual(docFields : dict):
    return false
    try:
        payload = {
           "name": getIdName(docFields),
           "datastoreId": DATASTORE_ID,
           "datasourceText": "[manual] " + docFields.get('html', ''),
           "type": "file",
           "config": {
               "tags": docFields.get('content_tags', []),
               "source_url": docFields.get('url', ''),
               "mime_type": "text/plain"
           }
        }

        resposta = requests.post(CHATVOLT_API_URL + "datasources", json=payload, headers=HEADERS_DESTINO)
        resposta.raise_for_status()
        print('Manual enviado com sucesso:', resposta.status_code)
    except requests.RequestException as e:
        print('Erro ao enviar manual:', e)

def getAll():
    response = requests.get(
        CHATVOLT_API_URL + "datastores/" + DATASTORE_ID,
        headers=HEADERS_DESTINO
    )
    response.raise_for_status()
    return response.json()

def delete(datasource):
    resposta = requests.delete(
        CHATVOLT_API_URL + "datasources/" + datasource,
        headers=HEADERS_DESTINO
    )
    resposta.raise_for_status()
    print('Dados deletados com sucesso:', resposta.status_code)

def getIdName(post : dict):
    return post.get("title", "") + " #" + post["id"]

def integrationStatus(chatVoltData, post):
    for index, data in enumerate(chatVoltData):
        if data["name"] == getIdName(post):
            dateChatVolt = parser.isoparse(data["updatedAt"])
            datePost = parser.isoparse(post["modification_date"])
            if dateChatVolt < datePost:
                return {"status": 2, "id": data["id"], "key" : index}
            else:
                return {"status": 3, "id": data["id"], "key" : index}
    return {"status": 1, "id": None, "key" : None}

def separar_perguntas_respostas(texto: str):
    frases = re.split(r'(?<=[?.!])\s+', texto.strip())

    perguntas = []
    respostas = []

    for frase in frases:
        frase = frase.strip()
        if not frase:
            continue
        if frase.endswith('?'):
            perguntas.append(frase)
        else:
            respostas.append(frase)

    return perguntas, respostas