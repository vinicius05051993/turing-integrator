import tools.sprinklr as sprinklr
from ai import Tags

def main():
    token = sprinklr.getToken()
    login = sprinklr.login(token)

    if login.get('responseCode', False) == 'SUCCESS':
        accessToken = login.get('accessToken', False)

        tags = Tags()

        for page in range(0, 1):
            spPosts = sprinklr.getPosts(accessToken, page)

            if len(spPosts) == 0:
                break

            for spPost in spPosts:
                print("Titulo: " + spPost['t'] + " tags:")
                print(tags.get(sprinklr.get_paragraph_texts(spPost['m'])))

if __name__ == '__main__':
    main()