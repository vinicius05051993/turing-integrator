import requests

CHATVOLT_API_URL = 'https://api.chatvolt.ai/'
DATASTORE_ID = 'cmbauo40600brx87n8gazln1j'

HEADERS_DESTINO = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 3f157bd4-64ae-4ecb-ac8d-ffe0f89b2149'
}

def send(docFields : dict):
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

def get():
    response = requests.get(
        CHATVOLT_API_URL + "datastores/" + DATASTORE_ID,
        headers=HEADERS_DESTINO
    )
    response.raise_for_status()
    return response.json()