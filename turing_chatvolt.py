import tools.turing as turing
import tools.chatvolt as chatvolt

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
            integration = chatvolt.integrationStatus(chatVoltDataSources, doc['fields'])

            if integration["key"] != None:
                chatVoltDataSources.pop(integration["key"])

            match integration['status']:
                case 1:
                    chatvolt.send(doc['fields'])
                case 2:
                    chatvolt.delete(integration['id'])
                    chatvolt.send(doc['fields'])

    for source in chatVoltDataSources:
        chatvolt.delete(source['id'])

if __name__ == '__main__':
    main()