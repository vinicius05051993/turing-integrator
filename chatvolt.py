import requests
from dateutil import parser

CHATVOLT_API_URL = 'https://api.chatvolt.ai/'
DATASTORE_ID = 'cmbauo40600brx87n8gazln1j'

HEADERS_DESTINO = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 3f157bd4-64ae-4ecb-ac8d-ffe0f89b2149'
}

def sendPost(docFields : dict):
    try:
        payload = {
           "name": getIdPostName(docFields),
           "datastoreId": DATASTORE_ID,
           "datasourceText": docFields.get('text', ''),
           "type": "file",
           "config": {
               "tags": docFields.get('tags', []),
               "source_url": docFields.get('url', ''),
               "mime_type": "text/plain"
           }
        }

        resposta = requests.post(CHATVOLT_API_URL + "datasources", json=payload, headers=HEADERS_DESTINO)
        resposta.raise_for_status()
        print('Dados enviados com sucesso:', resposta.status_code)
    except requests.RequestException as e:
        print('Erro ao enviar dados:', e)

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

def getIdPostName(post : dict):
    return post["title"] + " #" + post["id"]

def postIntegrationStatus(chatVoltData, post):
    for key, data in chatVoltData.items():
        if data["name"] == getIdPostName(post):
            dateChatVolt = parser.isoparse(data["updatedAt"])
            datePost = parser.isoparse(post["modification_date"])
            if dateChatVolt < datePost:
                return {"status": 2, "id": data["id"], "key" : key}
            else:
                return {"status": 3, "id": data["id"], "key" : key}
    return {"status": 1, "id": 0}