import tools.sprinklr as sprinklr
from ai import Tags
from ai import General

def main():
    token = sprinklr.getToken()
    login = sprinklr.login(token)

    if login.get('responseCode', False) == 'SUCCESS':
        accessToken = login.get('accessToken', False)

        tags = Tags()
        general = General()

        for page in range(0, 1):
            spPosts = sprinklr.getPosts(accessToken, page)

            if len(spPosts) == 0:
                break

            for spPost in spPosts:
                print('---------------')
                print("Titulo: " + spPost['t'])
                text = sprinklr.get_only_texts(spPost['m'])
                print(tags.get(text))
                question = "Voce é um especialista em conteudos da maple bear, seu trabalho é analisar detalhadamente o texto, interpretar para ter o contexto necessário para gerar TAGs objetivas e diretas. As Tags precisam ter no maximo 25 caracteres, as tags serão usadas para orientar nossa IA maple bear a buscar respostas corretas para os usuários."
                print(general.get(context=text, question=question))

if __name__ == '__main__':
    main()