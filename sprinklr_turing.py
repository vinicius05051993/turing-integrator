import tools.turing as turing
import tools.sprinklr as sprinklr

def main():
    token = sprinklr.getToken()
    login = sprinklr.login(token)

    if login.get('responseCode', False) == 'SUCCESS':
        accessToken = login.get('accessToken', False)

        allManualsTuring = turing.getAllTuringIds('manual')

        qtySprinklr = 0
        for page in range(0, 100):
            spPosts = sprinklr.getPosts(accessToken, page)
            qty = len(spPosts)

            qtySprinklr += qty

            if qty == 0:
                break

            for spPost in spPosts:
                integration = turing.integrationStatus(allManualsTuring, spPost)

                if "FAQ" in spPost['t']:
                    print(spPost)

                if integration["key"] != None:
                    allManualsTuring.pop(integration["key"])

                match integration['status']:
                    case 1:
                        turing.send(spPost)
                    case 2:
                        turing.delete(integration['id'])
                        turing.send(spPost)

        for manualTuringToDelete in allManualsTuring:
            turing.delete(manualTuringToDelete['id'])

        print("Total registros sprinklr: " + str(qtySprinklr))

if __name__ == '__main__':
    main()