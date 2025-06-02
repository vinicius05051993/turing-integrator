import requests
import os

CHATVOLT_API_URL = 'https://api.chatvolt.ai/'
DATASTORE_ID = 'cmbauo40600brx87n8gazln1j'

HEADERS_DESTINO = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 3f157bd4-64ae-4ecb-ac8d-ffe0f89b2149'
}

def getAllTuring(page):
    try:
        resposta = requests.get('https://busca.maplebear.com.br/api/sn/maplebear-prd-publish/search?p='+ str(page) +'&rows=100&_setlocale=pt_BR&nfpr=0&q=', verify=False)
        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException as e:
        print('Erro ao buscar dados:', e)
        return None

def sendPostToTuring(docFields : dict):
    try:
        payload = {
           "name": f"{docFields.get('title', '')} #{docFields.get('id', '')}",
           "datastoreId": DATASTORE_ID,
           "datasourceText": docFields.get('text', ''),
           "type": "file",
           "config": {
               "tags": docFields.get('tags', []),
               "source_url": docFields.get('source_url', ''),
               "mime_type": "text/plain"
           }
        }

        resposta = requests.post(CHATVOLT_API_URL + "datasources", json=payload, headers=HEADERS_DESTINO)
        resposta.raise_for_status()
        print('Dados enviados com sucesso:', resposta.status_code)
    except requests.RequestException as e:
        print('Erro ao enviar dados:', e)

def main():
    for page in range(1, 100):
        datas = getAllTuring(page)
        queryContext = datas.get("queryContext", {})
        if (page > queryContext['pageCount']):
            break

        document = datas.get("results", {}).get("document", [])
        for doc in document:
            print(str(page) + " " + doc['fields']['id'] + " - " + doc['fields']['mbtype'])
            sendToTuring(doc['fields'])
            break

        break

if __name__ == '__main__':
    main()