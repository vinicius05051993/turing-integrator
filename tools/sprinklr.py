import requests

UN_URL = 'https://care-api-prod2.sprinklr.com/care/community/jwt/un-authenticated/token'
UN_TOKEN = 'eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJQcmVTaGFyZWQgVG9rZW4gR2VuZXJhdGVkIGZyb20gQ29tbXVuaXR5IiwiYXVkIjpbIlNQUklOS0xSIl0sInNjb3BlIjpbIlJFQUQiLCJXUklURSJdLCJpc3MiOiJTUFJJTktMUiIsInR5cCI6IkpXVCIsImF1dGhUeXBlIjoiU1BSX1VOQVVUSEVOVElDQVRFRCIsInRva2VuVHlwZSI6IlBSRV9TSEFSRUQiLCJpYXQiOjE2NDg5Njg0MzcsImp0aSI6InNwcmlua2xyIn0.vDw5nFBTVR09GNmRTy4cn-4NkiNtmII3JKjxIJFVvkeBltAKPdpLujRgZbmfDgacrDiPt06HlT9Sw6gpOL7Idcdl-RmgEFX9-8VCtYnPvwnD0V6QwV-3nIbwCuQiAZvbFrmVVnlojfq6NjB1LHPlUEIzC3dQr4YHujyu6jGS2lyMyQq9XChKese91eYBad89q0FXGh_hQIAw6E7HHdyscHKexVIhhVURFRR28THpooiDehIhnKYUbr0pFGhg1KVHtej3l7CHtxUr561Z3lFy5E3Xqiag6jkpvhIUE2VYlR5Xcdx1KMitHx7qgObWVZU-HdLJrT3BTZ4Y0zFekpWeDQ'
PROJECT_ID = '2746bef7-54d2-4f0c-9fab-43175e1880ab'
LOGIN_URL = 'https://care-api-prod2.sprinklr.com/care/community/login'
URL_GET_POST = 'https://care-api-prod2.sprinklr.com/care/community/rest/un-authenticated/message/search-messages'
LOGIN_USERNAME = 'prodIntegracaoTuringxSprinklr'
LOGIN_PASSWORD = '6v2R$5OjXA.L'

FULL_URL_TOKEN = UN_URL + '?requestToken=' + UN_TOKEN + '&projectId=' + PROJECT_ID

HEADERS_DESTINO = {
    'Content-Type': 'application/json'
}

def getToken():
    response = requests.post(FULL_URL_TOKEN, headers=HEADERS_DESTINO)
    response.raise_for_status()
    print(response)
    return response