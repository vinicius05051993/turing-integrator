import tools.sprinklr as sprinklr

def main():
    token = sprinklr.getToken()
    login = sprinklr.login(token)
    print(login)

if __name__ == '__main__':
    main()