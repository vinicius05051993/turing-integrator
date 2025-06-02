import turing
import chatvolt

def main():
    chatVoltDatas = chatvolt.getAll()
    chatVoltDataSources = chatVoltDatas.get("datasources", {})

    for page in range(1, 100):
        datas = turing.getAllTuring(page)
        queryContext = datas.get("queryContext", {})
        if (page > queryContext['pageCount']):
            break

        document = datas.get("results", {}).get("document", [])
        for doc in document:
            if doc['fields']['mbtype'] == 'post':
                print(chatVoltDataSources)
                integration = chatvolt.postIntegrationStatus(chatVoltDataSources, doc['fields'])
                chatVoltDataSources.pop(integration["key"])
                print(chatVoltDataSources)
                match integration['status']:
                    case 1:
                        chatvolt.sendPost(doc['fields'])
                    case 2:
                        chatvolt.delete(integration['id'])
                        chatvolt.sendPost(doc['fields'])
                    case 3:
                        print('Nenhuma ação')
                    case 4:
                        chatvolt.delete(integration['id'])

            break
        break

if __name__ == '__main__':
    main()