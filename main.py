from dateutil import parser
import turing
import chatvolt

def main():
    chatVoltPost = chatvolt.get()
    print(chatVoltPost)
    chatVoltData = chatVoltPost.get("datasources", {})

    for page in range(1, 100):
        datas = turing.getAllTuring(page)
        queryContext = datas.get("queryContext", {})
        if (page > queryContext['pageCount']):
            break

        document = datas.get("results", {}).get("document", [])
        for doc in document:
            if doc['fields']['mbtype'] == 'post':
                match chatvolt.postIntegrationStatus(chatVoltData, doc['fields']):
                    case 1:
                        chatvolt.send(doc['fields'])
                    case 2:
                        print('Necessario atualizar')
                    case 3:
                        print('Nenhuma ação')

            break
        break

if __name__ == '__main__':
    main()