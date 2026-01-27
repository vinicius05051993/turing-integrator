import requests

def getPosts():
    url = "https://forms.maplebear.com.br/api/base-conhecimento/?format=json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def getPostDetails(kbPost):
    response = requests.get(kbPost['url_api'] + '?format=json')
    response.raise_for_status()
    return response.json()
