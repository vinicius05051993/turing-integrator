import tools.turing as turing
import tools.chatvolt as chatvolt
from ai import General

def main():
    chatVoltDatas = chatvolt.getAll()
    chatVoltDataSources = chatVoltDatas.get("datasources", {})

    generalAI = General()

    for page in range(1, 100):
        datas = turing.getAllTuring(page)
        queryContext = datas.get("queryContext", {})

        if (page > queryContext['pageCount']):
            break

        turingDatas = datas.get("results", {}).get("document", [])
        for turingData in turingDatas:
            if turingData['fields']['mbtype'] == 'post':
                statusInChatvolt = chatvolt.integrationStatus(chatVoltDataSources, turingData['fields'])

                if statusInChatvolt["key"] != None:
                    chatVoltDataSources.pop(statusInChatvolt["key"])

                match statusInChatvolt['status']:
                    case 1:
                        chatvolt.send(turingData['fields'], generalAI)
                    case 2:
#                         chatvolt.delete(statusInChatvolt['id'])

#     for chatVoltData in chatVoltDataSources:
#         chatvolt.delete(chatVoltData['id'])

if __name__ == '__main__':
    main()