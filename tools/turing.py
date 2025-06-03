import requests

def getAllTuring(page):
    try:
        resposta = requests.get('https://busca.maplebear.com.br/api/sn/maplebear-prd-publish/search?p='+ str(page) +'&rows=100&_setlocale=pt_BR&nfpr=0&q=', verify=False)
        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException as e:
        print('Erro ao buscar dados:', e)
        return None