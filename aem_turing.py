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

    # Parâmetros da busca
    params = {
        "path": root_path,
        "type": "dam:Asset",
        "property": "jcr:content/data/cq:model",
        "property.value": "content-fragment",
        "p.limit": "-1"
    }

    # Requisição
    response = requests.get(query_url, auth=HTTPBasicAuth(username, password), headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        print(data)
        hits = data.get("hits", [])
        print(f"Total de fragments encontrados: {len(hits)}\n")

        for hit in hits:
            dam_path = hit.get("path")  # Ex: /content/dam/maple-bear/posts/slm--2025

            if dam_path:
                # Converter para URL pública
                public_path = dam_path.replace("/content/dam", "/content")
                public_url = f"{public_url_prefix}{public_path}.html"

                print(f"🔗 URL pública: {public_url}")

                # (Opcional) buscar os dados estruturados do CF
                cf_json_url = f"{cms_url}{dam_path}.model.json"
                cf_response = requests.get(cf_json_url, auth=HTTPBasicAuth(username, password))

                if cf_response.status_code == 200:
                    cf_data = cf_response.json()
                    print("Dados do fragmento:")
                    print(cf_data)
                else:
                    print(f" Erro ao acessar o .model.json: {cf_response.status_code}")

                print("-" * 60)
    else:
        print(f"Erro ao buscar conteúdo: {response.status_code}")
        print(response.text)

if __name__ == '__main__':
    main()