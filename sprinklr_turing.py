import tools.sprinklr as sprinklr

def main():
    token = sprinklr.getToken()
    login = sprinklr.login(token)

    if login.get('responseCode', False) == 'SUCCESS':
        accessToken = login.get('accessToken', False)

        for page in range(999, 1000):
            spPosts = sprinklr.getPosts(accessToken, 0)
            for spPost in spPosts:
                print(spPost)

if __name__ == '__main__':
    main()