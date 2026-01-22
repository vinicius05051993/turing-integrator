import requests
import time

author_url = "https://author-p120717-e1174076.adobeaemcloud.com"
credentials = ("turing_user", "5DIzbK4@")

dam_folder = "/content/dam/maple-bear/manuais"

# ⚠️ ajuste para o model certo
model_path = "/conf/maple-bear/settings/dam/cfm/models/manuais"

fragment_name = f"manual-{int(time.time())}"

fields = {
    "title": "Manual criado via API",
    "description": "Criado automaticamente"
}

def get_csrf_token(session: requests.Session):
    url = author_url + "/libs/granite/csrf/token.json"
    r = session.get(url)
    print("CSRF token status:", r.status_code)
    r.raise_for_status()
    return r.json()["token"]

def create_fragment(session: requests.Session):
    url = author_url + dam_folder

    payload = {
        ":operation": "create",
        ":name": fragment_name,
        "jcr:primaryType": "dam:Asset",
        "jcr:content/jcr:primaryType": "dam:AssetContent",
        "jcr:content/contentFragment": "true",
        "jcr:content/data/cq:model": model_path,
    }

    resp = session.post(url, data=payload)

    print("CREATE status:", resp.status_code)
    print("CREATE response text:", resp.text[:2000])  # corta pra não explodir o log

    if resp.status_code not in (200, 201):
        raise Exception(f"Erro ao criar fragmento. HTTP {resp.status_code}")

    return f"{dam_folder}/{fragment_name}"

def fill_fields(session: requests.Session, fragment_path: str):
    url = author_url + fragment_path + "/jcr:content/data/master"

    resp = session.post(url, data=fields)

    print("FILL status:", resp.status_code)
    print("FILL response text:", resp.text[:2000])

    if resp.status_code not in (200, 201):
        raise Exception(f"Erro ao preencher campos. HTTP {resp.status_code}")

def main():
    session = requests.Session()
    session.auth = credentials

    csrf = get_csrf_token(session)
    session.headers.update({"CSRF-Token": csrf})

    fragment_path = create_fragment(session)
    print("Fragment criado em:", fragment_path)

    fill_fields(session, fragment_path)
    print("OK - campos preenchidos")

if __name__ == "__main__":
    main()
