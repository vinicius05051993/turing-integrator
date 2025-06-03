import requests
import re

UN_URL = 'https://care-api-prod2.sprinklr.com/care/community/jwt/un-authenticated/token'
UN_TOKEN = 'eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJQcmVTaGFyZWQgVG9rZW4gR2VuZXJhdGVkIGZyb20gQ29tbXVuaXR5IiwiYXVkIjpbIlNQUklOS0xSIl0sInNjb3BlIjpbIlJFQUQiLCJXUklURSJdLCJpc3MiOiJTUFJJTktMUiIsInR5cCI6IkpXVCIsImF1dGhUeXBlIjoiU1BSX1VOQVVUSEVOVElDQVRFRCIsInRva2VuVHlwZSI6IlBSRV9TSEFSRUQiLCJpYXQiOjE2NDg5Njg0MzcsImp0aSI6InNwcmlua2xyIn0.vDw5nFBTVR09GNmRTy4cn-4NkiNtmII3JKjxIJFVvkeBltAKPdpLujRgZbmfDgacrDiPt06HlT9Sw6gpOL7Idcdl-RmgEFX9-8VCtYnPvwnD0V6QwV-3nIbwCuQiAZvbFrmVVnlojfq6NjB1LHPlUEIzC3dQr4YHujyu6jGS2lyMyQq9XChKese91eYBad89q0FXGh_hQIAw6E7HHdyscHKexVIhhVURFRR28THpooiDehIhnKYUbr0pFGhg1KVHtej3l7CHtxUr561Z3lFy5E3Xqiag6jkpvhIUE2VYlR5Xcdx1KMitHx7qgObWVZU-HdLJrT3BTZ4Y0zFekpWeDQ'
PROJECT_ID = '2746bef7-54d2-4f0c-9fab-43175e1880ab'
LOGIN_URL = 'https://care-api-prod2.sprinklr.com/care/community/login'
URL_GET_POST = 'https://care-api-prod2.sprinklr.com/care/community/rest/un-authenticated/message/search-messages'
LOGIN_USERNAME = 'prodIntegracaoTuringxSprinklr'
LOGIN_PASSWORD = '6v2R$5OjXA.L'

FULL_URL_TOKEN = UN_URL + '?requestToken=' + UN_TOKEN + '&projectId=' + PROJECT_ID

def getToken():
    header = {
        'Content-Type': 'application/json'
    }
    response = requests.post(FULL_URL_TOKEN, headers=header)
    response.raise_for_status()
    return response.text

def login(token):
    header = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'username': LOGIN_USERNAME,
        'password': LOGIN_PASSWORD,
        'X-Community-Authorization': 'Bearer ' + token
    }

    response = requests.post(LOGIN_URL, headers=header)
    response.raise_for_status()
    return response.json()

def getPosts(accessToken, page):
    headers = {
        'Content-Type': 'application/json',
        'X-Community-Authorization': 'Bearer ' + accessToken
    }

    data = {
        "filters": [
            {
                "field": "mSTp",
                "filterType": "IN",
                "values": ["13"]
            }
        ],
        "page": {
            "page": page,
            "size": 10
        },
        "sorts": [
            {
                "key": "cTm",
                "order": "DESC"
            }
        ]
    }

    response = requests.post(
        URL_GET_POST,
        headers=headers,
        json=data
    )

    return response.json().get("data", [])

def get_paragraph_texts(html: str) -> str:
    text_captured = ''

    # Find all text within <span> or <p> tags
    matches = re.findall(r'<(?:span|p)[^>]*>(.*?)</(?:span|p)>', html, flags=re.IGNORECASE | re.DOTALL)

    if matches:
        text_captured = ' '.join(matches)

    # Remove any remaining HTML tags and non-alphanumeric characters except spaces
    text_captured = re.sub(r'<[^>]*>', '', text_captured)  # Remove any remaining tags
    text_captured = re.sub(r'[^\w\s]', '', text_captured)  # Remove non-alphanumeric chars

    return text_captured.strip()
