import tools.sprinklr as sprinklr

def main():
    token = sprinklr.getToken()
    login = sprinklr.login(token)

    if login.get('responseCode', False) == 'SUCCESS':
        accessToken = login.get('accessToken', False)
        posts = sprinklr.getPosts(accessToken)
        print(posts)

if __name__ == '__main__':
    main()