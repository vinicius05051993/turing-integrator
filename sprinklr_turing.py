import tools.turing as turing
import tools.sprinklr as sprinklr

def main():
    token = sprinklr.getToken()
    login = sprinklr.login(token)

    if login.get('responseCode', False) == 'SUCCESS':
        accessToken = login.get('accessToken', False)

        allManualsTuring = turing.getAllTuringIds('manual')

        idToDelete = False

        qtySprinklr = 0
        for page in range(0, 100):
            spPosts = sprinklr.getPosts(accessToken, page)
            qty = len(spPosts)

            qtySprinklr += qty

            if qty == 0:
                break

            for spPost in spPosts:
                integration = turing.integrationStatus(allManualsTuring, spPost)
                idToDelete = integration['id']

                allManualsTuring = [
                    ds for ds in allManualsTuring
                    if ds["id"] != integration['id']
                ]

                match integration['status']:
                    case 1:
#                         turing.delete(spPost['id'], False)
                        turing.send(spPost)

        for manualTuringToDelete in allManualsTuring[:1]:
            turing.delete(manualTuringToDelete['id'], True)
        else:
            if idToDelete:
                turing.delete(idToDelete, False)

        print("Total registros sprinklr: " + str(qtySprinklr))

if __name__ == '__main__':
    main()