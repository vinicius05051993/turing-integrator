import tools.sprinklr as sprinklr

def main():
    token = sprinklr.getToken()
    login = sprinklr.login(token)

    if login.get('responseCode', False) == 'SUCCESS':
        accessToken = login.get('accessToken', False)

        for page in range(1, 2):
            posts = sprinklr.getPosts(accessToken, 0)
            for post in posts:
                print(post)

if __name__ == '__main__':
    main()