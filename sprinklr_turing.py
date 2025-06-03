import tools.sprinklr as sprinklr
from ai import ExtratorPalavrasChave

def main():
    token = sprinklr.getToken()
    login = sprinklr.login(token)

    if login.get('responseCode', False) == 'SUCCESS':
        accessToken = login.get('accessToken', False)

        extrator = ExtratorPalavrasChave()

        for page in range(0, 100):
            spPosts = sprinklr.getPosts(accessToken, page)

            if len(spPosts) == 0:
                break

            for spPost in spPosts:
                print("Titulo: " + spPost['t'] + " tags: " + extrator.extrair_palavras_chave(spPost['m']))

if __name__ == '__main__':
    main()