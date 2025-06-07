import requests
from dateutil import parser
import re
import json

CHATVOLT_API_URL = 'https://api.chatvolt.ai/'
DATASTORE_ID = 'cmbauo40600brx87n8gazln1j'
TOKEN = '3f157bd4-64ae-4ecb-ac8d-ffe0f89b2149'

HEADERS_DESTINO = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + TOKEN
}

def send(docFields : dict):
    match docFields.get('mbtype', False):
        case 'post':
            sendPost(docFields)
        case 'event':
            sendEvent(docFields)
        case 'manual':
            if "FAQ" in docFields.get('content_tags', ""):
                sendFAQ(docFields)
            else:
                sendManual(docFields)

def sendPost(docFields : dict):
    try:
        payload = {
           "name": getIdName(docFields),
           "datastoreId": DATASTORE_ID,
           "datasourceText": "[post] " + docFields.get('text', ''),
           "type": "file",
           "config": {
               "tags": docFields.get('content_tags', "").split('\n'),
               "source_url": docFields.get('url', ''),
               "mime_type": "text/plain"
           }
        }

        resposta = requests.post(CHATVOLT_API_URL + "datasources", json=payload, headers=HEADERS_DESTINO)
        resposta.raise_for_status()
        print('Publicação enviada com sucesso:', resposta.status_code, json.dumps(payload))
    except requests.RequestException as e:
        print('Erro ao enviar publicação:', e, json.dumps(payload))

def sendEvent(docFields : dict):
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
               "tags": docFields.get('content_tags', "").split('\n'),
               "source_url": docFields.get('url', ''),
               "mime_type": "text/plain"
           }
        }

        resposta = requests.post(CHATVOLT_API_URL + "datasources", json=payload, headers=HEADERS_DESTINO)
        resposta.raise_for_status()
        print('Evento enviado com sucesso:', resposta.status_code, json.dumps(payload))
    except requests.RequestException as e:
        print('Erro ao enviar eventos:', e, json.dumps(payload))

def sendFAQ(docFields : dict):
    try:
        blocks = separar_perguntas_respostas(docFields['html'])
        for i, block in enumerate(blocks):
            payload = {
               "name": getIdName(docFields) + " - " + str(i),
               "datastoreId": DATASTORE_ID,
               "datasourceText": "[faq] " + '\n'.join(block['respostas']),
               "type": "qa",
               "isUpdateText": True,
               "config": {
                   "tags": docFields.get('content_tags', "").split('\n'),
                   "source_url": docFields.get('url', ''),
                   "question": getMarkArea(docFields) + '\n'.join(block['perguntas']),
                   "answer": '\n'.join(block['respostas'])
               }
            }

            resposta = requests.post(CHATVOLT_API_URL + "datasources", json=payload, headers=HEADERS_DESTINO)
            resposta.raise_for_status()
            print('FAQ enviado com sucesso:', resposta.status_code, json.dumps(payload))
    except requests.RequestException as e:
        print('Erro ao enviar FAQ:', e, json.dumps(payload))

def sendManual(docFields : dict):
    try:
        payload = {
           "name": getIdName(docFields),
           "datastoreId": DATASTORE_ID,
           "datasourceText": "[manual] " + docFields.get('html', ''),
           "type": "file",
           "config": {
               "tags": docFields.get('content_tags', "").split('\n'),
               "source_url": docFields.get('url', ''),
               "mime_type": "text/plain"
           }
        }

        resposta = requests.post(CHATVOLT_API_URL + "datasources", json=payload, headers=HEADERS_DESTINO)
        resposta.raise_for_status()
        print('Manual enviado com sucesso:', resposta.status_code, json.dumps(payload))
    except requests.RequestException as e:
        print('Erro ao enviar manual:', e, json.dumps(payload))

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
    if post.get('area_name', False):
        return getMarkArea(post) + post.get("title", "") + " #" + post["id"]
    else:
        return post.get("title", "") + " #" + post["id"]

def getMarkArea(docFields):
    return '['+ docFields.get('area_name', "") +'] '

def integrationStatus(chatVoltDatas, turingData):
    for index, chatVoltData in enumerate(chatVoltDatas):
        if getIdName(turingData) in chatVoltData["name"] or getIdName(turingData) == chatVoltData["name"]:
            dateChatVolt = parser.isoparse(chatVoltData["updatedAt"])
            datePost = parser.isoparse(turingData["modification_date"])
            if dateChatVolt < datePost:
                return {"status": 2, "id": chatVoltData["id"], "key" : index}
            else:
                return {"status": 3, "id": chatVoltData["id"], "key" : index}
    return {"status": 1, "id": None, "key" : None}

def separar_perguntas_respostas(texto: str):
    blocos = re.split(r'(?i)\bPerguntas\b', texto)
    resultado = []

    for bloco in blocos:
        if not bloco.strip():
            continue

        partes = re.split(r'(?i)\bRespostas?\b', bloco)
        perguntas_brutas = partes[0].strip() if len(partes) >= 1 else ''
        respostas_brutas = partes[1].strip() if len(partes) > 1 else ''

        perguntas = re.findall(r'[^?]+\?', perguntas_brutas)
        respostas = [r.strip() for r in respostas_brutas.split('\n') if r.strip()]

        resultado.append({
            'perguntas': [p.strip() for p in perguntas],
            'respostas': respostas
        })

    return resultado