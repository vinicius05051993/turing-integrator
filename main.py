import requests
import os
from dateutil import parser
import turing

CHATVOLT_API_URL = 'https://api.chatvolt.ai/'
DATASTORE_ID = 'cmbauo40600brx87n8gazln1j'

HEADERS_DESTINO = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 3f157bd4-64ae-4ecb-ac8d-ffe0f89b2149'
}

def sendPostToChatVolt(docFields : dict):
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

def getDataChatVolt():
    response = requests.get(
        CHATVOLT_API_URL + "datastores/" + DATASTORE_ID,
        headers=HEADERS_DESTINO
    )
    response.raise_for_status()
    return response.json()

def getIdPostName(post : dict):
    return post["title"] + " #" + post["id"]

def postIntegrationStatus(chatVoltData, post):
    for data in chatVoltData:
        if data["name"] == getIdPostName(post):
            dateChatVolt = parser.isoparse(data["updatedAt"])
            datePost = parser.isoparse(post["modification_date"])
            if dateChatVolt < datePost:
                return 2
            else:
                return 3
    return 1


def main():
    chatVoltPost = getDataChatVolt()
    print(chatVoltPost)
    chatVoltData = chatVoltPost.get("datasources", {})

    for page in range(1, 100):
        datas = turing.getAllTuring(page)
        queryContext = datas.get("queryContext", {})
        if (page > queryContext['pageCount']):
            break

        document = datas.get("results", {}).get("document", [])
        for doc in document:
            if doc['fields']['mbtype'] == 'post':
                match postIntegrationStatus(chatVoltData, doc['fields']):
                    case 1:
                        sendPostToChatVolt(doc['fields'])
                    case 2:
                        print('Necessario atualizar')
                    case 3:
                        print('Nenhuma ação')

            break
        break

if __name__ == '__main__':
    main()