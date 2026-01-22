import requests
import json
import time

# Config
author_url = "https://author-p120717-e1174076.adobeaemcloud.com"
credentials = ("turing_user", "5DIzbK4@")

project = "maple-bear"
model_name = "manuais"

# ✅ Pasta correta (manuais)
dam_folder = f"/content/dam/{project}/manuais"

# Nome do fragmento (nome do asset no DAM)
fragment_name = f"manual-{int(time.time())}"

# Path do model
model_path = f"/conf/{project}/settings/dam/cfm/models/{model_name}"

# Campos do modelo (ajuste conforme seu model "manual")
fields = {
    "title": "Manual criado via API",
    "description": "Esse manual foi criado automaticamente via API."
}

def create_fragment():
    url = author_url + dam_folder

    payload = {
        ":operation": "create",
        ":name": fragment_name,

        "jcr:primaryType": "dam:Asset",
        "jcr:content/jcr:primaryType": "dam:AssetContent",
        "jcr:content/contentFragment": "true",

        # aponta pro model do CF
        "jcr:content/data/cq:model": model_path,
    }

    resp = requests.post(url, data=payload, auth=credentials)

    if resp.status_code not in (200, 201):
        raise Exception(
            f"❌ Erro ao criar fragmento. HTTP {resp.status_code}\n{resp.text}"
        )

    fragment_path = f"{dam_folder}/{fragment_name}"
    print("✅ Fragmento criado:", fragment_path)
    return fragment_path

def fill_fragment_fields(fragment_path):
    url = author_url + fragment_path + "/jcr:content/data/master"

    resp = requests.post(url, data=fields, auth=credentials)

    if resp.status_code not in (200, 201):
        raise Exception(
            f"❌ Erro ao preencher campos. HTTP {resp.status_code}\n{resp.text}"
        )

    print("✅ Campos preenchidos com sucesso!")

def get_fragment_json(fragment_path):
    url = author_url + fragment_path + "/jcr:content/data/master.json"
    resp = requests.get(url, auth=credentials)

    if resp.status_code != 200:
        raise Exception(
            f"❌ Erro ao ler fragmento. HTTP {resp.status_code}\n{resp.text}"
        )

    print("📄 Conteúdo do fragmento:")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))

def main():
    fragment_path = create_fragment()
    fill_fragment_fields(fragment_path)
    get_fragment_json(fragment_path)

if __name__ == "__main__":
    main()
