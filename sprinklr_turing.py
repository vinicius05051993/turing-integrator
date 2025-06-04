import tools.sprinklr as sprinklr
import tools.turing as turing
# from ai import General

def main():
    token = sprinklr.getToken()
    login = sprinklr.login(token)

    if login.get('responseCode', False) == 'SUCCESS':
        accessToken = login.get('accessToken', False)

#         general = General()
        allTuringIds = turing.getAllTuringIds('manual')

        for page in range(0, 2):
            spPosts = sprinklr.getPosts(accessToken, page)

            if len(spPosts) == 0:
                break

            for spPost in spPosts:
                integration = turing.integrationStatus(allTuringIds, spPost)

                if integration["key"] != None:
                    allTuringIds.pop(integration["key"])

                match integration['status']:
                    case 1:
                        turing.send(spPost)
                    case 2:
                        turing.delete(integration['id'])
                        turing.send(spPost)


#                 print('---------------')
#                 print("Titulo: " + spPost['t'])
#                 text = sprinklr.get_only_texts(spPost['m'])
#                 question = "Analise detalhadamente o texto e interprete para ter o contexto necessário para gerar TAGs objetivas. As Tags precisam ter no maximo 25 caracteres, separadas por virula."
#                 print(general.get(context=text, question=question))

if __name__ == '__main__':
    main()