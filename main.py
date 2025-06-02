import requests
import os

API_DESTINO = 'https://api.destino.com/receber'

HEADERS_DESTINO = {
    'Content-Type': 'application/json'
}

def getAllTuring(page):
    try:
        resposta = requests.get('https://busca.maplebear.com.br/api/sn/maplebear-prd-publish/search?p='+ str(page) +'&rows=100&_setlocale=pt_BR&nfpr=0&q=', verify=False)
        resposta.raise_for_status()
        dados = resposta.json()
        return dados
    except requests.RequestException as e:
        print('Erro ao buscar dados:', e)
        return None

def enviar_dados(dados):
    try:
        resposta = requests.post(API_DESTINO, json=dados, headers=HEADERS_DESTINO)
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


if __name__ == '__main__':
    main()