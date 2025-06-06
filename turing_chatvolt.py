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

        turingDatas = datas.get("results", {}).get("document", [])
        turingDatas = []
        for turingData in turingDatas:
            integration = chatvolt.integrationStatus(chatVoltDataSources, turingData['fields'])

            if integration["key"] != None:
                chatVoltDataSources.pop(integration["key"])

            match integration['status']:
                case 1:
                    chatvolt.send(turingData['fields'])
                case 2:
                    chatvolt.delete(integration['id'])
                    chatvolt.send(turingData['fields'])

    for source in chatVoltDataSources:
        chatvolt.delete(source['id'])

if __name__ == '__main__':
    main()