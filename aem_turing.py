import requests
from requests.auth import HTTPBasicAuth

# Configurações
cms_url = "https://author-p120717-e1174076.adobeaemcloud.com"
username = "turing_user"
password = "5DIzbK4@"
root_path = "/content/dam/maple-bear"

# Cabeçalhos para JSON
headers = {
    "Accept": "application/json"
}

def main():
    query_url = f"{cms_url}/bin/querybuilder.json"

    params = {
        "path": root_path,
        "type": "dam:Asset",
        "property": "jcr:content/data/cq:model",
        "property.value": "content-fragment",
        "p.limit": "-1"  # sem limite de resultados
    }

    response = requests.get(query_url, auth=HTTPBasicAuth(username, password), headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        hits = data.get("hits", [])
        print(f"Total de fragments encontrados: {len(hits)}\n")

        for hit in hits:
            path = hit.get("path")
            if path:
                cf_json_url = f"{cms_url}{path}.model.json"
                cf_response = requests.get(cf_json_url, auth=HTTPBasicAuth(username, password))
                if cf_response.status_code == 200:
                    cf_data = cf_response.json()
                    print(f"📄 Fragmento: {path}")
                    print(cf_data)
                    print("-" * 40)
                else:
                    print(f"❌ Erro ao acessar {cf_json_url} — Status: {cf_response.status_code}")
    else:
        print(f"❌ Falha ao buscar conteúdo. Status: {response.status_code}")
        print(response.text)

if __name__ == '__main__':
    main()