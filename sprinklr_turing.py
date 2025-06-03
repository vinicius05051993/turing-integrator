import tools.sprinklr as sprinklr

def main():
    token = sprinklr.getToken()
    login = sprinklr.login(token)

    if login.get('responseCode', False) == 'SUCCESS':
        accessToken = login.get('accessToken', False)

        for page in range(0, 100):
            spPosts = sprinklr.getPosts(accessToken, page)

            if len(spPosts) == 0:
                break

            print("Page: " + str(page))
            for spPost in spPosts:
                print("----")

if __name__ == '__main__':
    main()