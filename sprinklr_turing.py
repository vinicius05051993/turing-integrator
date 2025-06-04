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
                print("Titulo: " + spPost['t'])
                text = sprinklr.get_only_texts(spPost['m'])
                print(tags.get(text))
                print(general.get(context=text, question='Qual a principal ideia?'))

if __name__ == '__main__':
    main()