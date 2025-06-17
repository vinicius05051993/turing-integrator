import tools.turing as turing
import tools.sprinklr as sprinklr

def main():
    token = sprinklr.getToken()
    login = sprinklr.login(token)

    if login.get('responseCode', False) == 'SUCCESS':
        accessToken = login.get('accessToken', False)

        allManualsTuring = turing.getAllTuringIds('manual')

        qtySprinklr = 0
        qtyTuring = 0
        lastTuringId = False
        for page in range(0, 1):
            spPosts = sprinklr.getPosts(accessToken, page)
            qty = len(spPosts)

            qtySprinklr += qty

            if qty == 0:
                break

            for spPost in spPosts:
                integration = turing.integrationStatus(allManualsTuring, spPost)

                if integration["key"] != None:
                    lastTuringId = integration['id']
                    allManualsTuring.pop(integration["key"])

                match integration['status']:
                    case 1:
                        turing.send(spPost)
                        qtyTuring += 1
                    case 2:
                        turing.delete(integration['id'])

        if len(allManualsTuring) == 0 and lastTuringId:
            turing.delete(lastTuringId)

        for manualTuringToDelete in allManualsTuring:
            turing.delete(manualTuringToDelete['id'])

        print("Total registros sprinklr: " + str(qtySprinklr))
        print("Total registros enviados turing: " + str(qtyTuring))

if __name__ == '__main__':
    main()