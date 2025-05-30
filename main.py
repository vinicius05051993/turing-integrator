import requests
import os

API_ORIGEM = 'https://busca.maplebear.com.br/api/sn/maplebear-prd-publish/search?p=1&sort=publication_date:desc&rows=240&_setlocale=pt_BR&nfpr=0&fq[]=mbtype:manual&q='
API_DESTINO = 'https://api.destino.com/receber'

HEADERS_DESTINO = {
    'Content-Type': 'application/json'
}

def getManuals():
    try:
        resposta = requests.get(API_ORIGEM, verify=False)
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
    manuals = getManuals()
    if manuals:
        document = manuals.get("results", {}).get("document", [])
        for doc in document:
            print(doc['fields']['id'])

if __name__ == '__main__':
    main()