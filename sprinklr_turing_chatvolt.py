import tools.turing as turing
import tools.sprinklr as sprinklr
import tools.chatvolt as chatvolt

def main():
    token = sprinklr.getToken()
    login = sprinklr.login(token)

    if login.get('responseCode', False) == 'SUCCESS':
        accessToken = login.get('accessToken', False)

        allManualsTuring = turing.getAllTuringIds('manual')

        chatVoltDatas = chatvolt.getAll()
        chatVoltDataSources = chatVoltDatas.get("datasources", {})

        qtySprinklr = 0
        for page in range(0, 100):
            spPosts = sprinklr.getPosts(accessToken, page)
            qty = len(spPosts)

            qtySprinklr += qty

            if qty == 0:
                break

            for spPost in spPosts:
                integration = turing.integrationStatus(allManualsTuring, spPost)

                allManualsTuring = [
                    ds for ds in allManualsTuring
                    if ds["id"] != integration['id']
                ]

                match integration['status']:
                    case 1:
                        turingFields = turing.send(spPost)

                        if "FAQ" in turingFields.get('title', ''):
                            statusInChatvolt = chatvolt.integrationStatusFAQ(chatVoltDataSources, turingFields)
                            idsParaRemover = set(statusInChatvolt['allChatVoltsFaqIds'])
            
                            chatVoltDataSources = [
                                ds for ds in chatVoltDataSources
                                if ds["id"] not in idsParaRemover
                            ]
            
                            match statusInChatvolt['status']:
                                case 1:
                                    chatvolt.send(turingFields, False)
                                case 2:
                                    for chatVoltsFaqId in statusInChatvolt['allChatVoltsFaqIds']:
                                        chatvolt.delete(chatVoltsFaqId)
                                    chatvolt.send(turingFields, False)
                        else:
                            statusInChatvolt = chatvolt.integrationStatus(chatVoltDataSources, turingFields)
            
                            if statusInChatvolt["key"] != None:
                                chatVoltDataSources.pop(statusInChatvolt["key"])
            
                            match statusInChatvolt['status']:
                                case 1:
                                    chatvolt.send(turingFields, False)
                                case 2:
                                    chatvolt.delete(statusInChatvolt['id'])
                                    chatvolt.send(turingFields, False)

#         for chatVoltData in chatVoltDataSources[:1]:
#             chatvolt.delete(chatVoltData['id'])

        for manualTuringToDelete in allManualsTuring[:1]:
            turing.delete(manualTuringToDelete['id'], True)

        print("Total registros sprinklr: " + str(qtySprinklr))

if __name__ == '__main__':
    main()