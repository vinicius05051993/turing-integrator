import requests

def getAllTuring(page):
    try:
        resposta = requests.get('https://busca.maplebear.com.br/api/sn/maplebear-prd-publish/search?p='+ str(page) +'&rows=100&_setlocale=pt_BR&nfpr=0&q=', verify=False)
        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException as e:
        print('Erro ao buscar dados:', e)
        return None

def getAllTuringIds():
    ids = []
    for page in range(1, 100):
        datas = getAllTuring(page)
        queryContext = datas.get("queryContext", {})

        if (page > queryContext['pageCount']):
            break

        document = datas.get("results", {}).get("document", [])
        for doc in document:
            ids.append({'id': doc['fields']['id'], 'last_update': doc['fields']['modification_date']})

    return ids

def integrationStatus(allTuringIds, spPost):
    for index, turingData in enumerate(allTuringIds):
        if turingData['id'] == spPost['id']:
            dateTuring = parser.isoparse(turingData['last_update'])
            dateSpPost = parser.isoparse(spPost["modification_date"])
            if dateTuring < dateSpPost:
                return {"status": 2, "id": turingData["id"], "key" : index}
            else:
                return {"status": 3, "id": turingData["id"], "key" : index}
    return {"status": 1, "id": None, "key" : None}

def send(spPost):
    print("Enviar para turing")

def delete(id):
    print("Deletar no turing")