import tools.sprinklr as sprinklr

def main():
    token = sprinklr.getToken()
    login = sprinklr.login(token)

    if login.get('responseCode', False) == 'SUCCESS':
        accessToken = login.get('accessToken', False)

        for page in range(0, 100):
            spPosts = sprinklr.getPosts(accessToken, page)
            print("Page: " + page)
            for spPost in spPosts:
                print(spPost)

if __name__ == '__main__':
    main()