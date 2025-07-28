import requests

# 1. Configurações
author_url = "https://author-p120717-e1174076.adobeaemcloud.com"
public_url_base = "https://portal.maplebear.com.br"
query_path = "/bin/querybuilder.json"
credentials = ("turing_user", "5DIzbK4@")  # coloque seu login do AEM Author

# 2. Parâmetros para buscar páginas publicadas
params = {
    "path": "/content/maple-bear",
    "type": "cq:Page",
    "property": "jcr:content/cq:lastReplicationAction",
    "property.value": "Activate",
    "p.limit": "-1",
    "orderby": "path"
}

# 3. Faz a requisição ao Query Builder
response = requests.get(author_url + query_path, params=params, auth=credentials)

if response.status_code != 200:
    print("Erro ao consultar páginas:", response.status_code, response.text)
    exit()

data = response.json()
hits = data.get("hits", [])

# 4. Gera URLs públicas e consulta HTML
for hit in hits:
    path = hit.get("path", "")
    if not path.startswith("/content/maple-bear"):
        continue

    # Remove '/content/maple-bear' e monta URL pública
    relative_path = path.replace("/content/maple-bear", "")
    if relative_path.endswith("/jcr:content"):
        relative_path = relative_path.replace("/jcr:content", "")

    page_url = f"{public_url_base}{relative_path}.html"

    try:
        html_response = requests.get(page_url, timeout=10)
        print(f"\n✅ {page_url} - Status: {html_response.status_code}")
        print(html_response.text[:200])  # imprime os primeiros 200 caracteres
    except Exception as e:
        print(f"❌ Erro ao acessar {page_url}: {e}")
