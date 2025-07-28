import requests
from requests.auth import HTTPBasicAuth

CMS_URL = "https://author-p120717-e1174076.adobeaemcloud.com"
USERNAME = "turing_user"
PASSWORD = "5DIzbK4@"

ROOT_PATH = "/content/maple-bear"
PUBLISH_URL_PREFIX = "https://portal.maplebear.com.br"

def get_pages(path):
    url = f"{CMS_URL}{path}.infinity.json"
    resp = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    data = resp.json()

    pages = []

    def walk(node, current_path):
        if isinstance(node, dict):
            if node.get("jcr:primaryType") == "cq:Page":
                pages.append(current_path)
            for key, value in node.items():
                if isinstance(value, dict):
                    walk(value, f"{current_path}/{key}")

    walk(data, ROOT_PATH)
    return pages

def get_html(url):
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.text
    return None

if __name__ == "__main__":
    pages = get_pages(ROOT_PATH)
    for path in pages:
        public_url = f"{PUBLISH_URL_PREFIX}{path.replace('/content/maple-bear', '')}.html"
        print(f"Fetching: {public_url}")
        html = get_html(public_url)
        if html:
            print(f"✔️ Fetched HTML for {public_url}")
        else:
            print(f"❌ Failed to fetch {public_url}")
