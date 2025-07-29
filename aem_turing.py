import tools.aem as aem
import tools.turing as turing

def main():
    for page in range(1, 2):
        datas = turing.getAllTuring(page)
        queryContext = datas.get("queryContext", {})

        if (page > queryContext['pageCount']):
            break

        turingDatas = datas.get("results", {}).get("document", [])
        for turingData in turingDatas:
            if turingData['fields'].get('mbtype', '') == "post":
                pageContent = aem.getPageOfPost(turingData['fields']['id'])
                if pageContent:
                    textContent = aem.find_all_objects(pageContent)
                    turingData['fields']['text'] = " ".join(textContent)

                    turing.delete(turingData['fields']['id'])
                    turing.sendOnlyFields(turingData['fields'])
                    break

if __name__ == '__main__':
    main()
