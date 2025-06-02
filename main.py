import turing
import chatvolt

def main():
    chatVoltDatas = chatvolt.getAll()
    chatVoltDataSources = chatVoltDatas.get("datasources", {})
    print(chatVoltDataSources)

    for page in range(1, 100):
        datas = turing.getAllTuring(page)
        queryContext = datas.get("queryContext", {})
        if (page > queryContext['pageCount']):
            break

        document = datas.get("results", {}).get("document", [])
        for doc in document:
            if doc['fields']['mbtype'] == 'post':
                integration = chatvolt.postIntegrationStatus(chatVoltDataSources, doc['fields'])

                if integration["key"] != None:
                    chatVoltDataSources.pop(integration["key"])

                for source in chatVoltDataSources:
                    chatvolt.delete(source['id'])

                match integration['status']:
                    case 1:
                        chatvolt.sendPost(doc['fields'])
                    case 2:
                        chatvolt.delete(integration['id'])
                        chatvolt.sendPost(doc['fields'])

            break
        break

if __name__ == '__main__':
    main()