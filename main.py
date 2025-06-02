import turing
import chatvolt

def main():
    chatVoltPost = chatvolt.get()
    print(chatVoltPost)
    chatVoltDataSources = chatVoltPost.get("datasources", {})

    for page in range(1, 100):
        datas = turing.getAllTuring(page)
        queryContext = datas.get("queryContext", {})
        if (page > queryContext['pageCount']):
            break

        document = datas.get("results", {}).get("document", [])
        for doc in document:
            if doc['fields']['mbtype'] == 'post':
                integration = chatvolt.postIntegrationStatus(chatVoltDataSources, doc['fields'])
                match integration['status']:
                    case 1:
                        chatvolt.send(doc['fields'])
                    case 2:
                        print('Necessario atualizar')
                    case 3:
                        print('Nenhuma ação')
                    case 4:
                        chatvolt.delete(integration['id'])

            break
        break

if __name__ == '__main__':
    main()