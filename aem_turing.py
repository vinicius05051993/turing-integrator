import tools.aem as aem
import tools.turing as turing

def main():
    allContentFragment = aem.getAllContentFragment()
    allPostsTuring =  turing.getAllTuringIds('post')

    for contentFragment in allContentFragment:
        id = contentFragment['path']
        if aem.isPost(id):
            proprieties = aem.getContentFragmentProprieties(id)
            pageContent = aem.getPageContent(id)
            if proprieties and pageContent:
                integration = aem.integrationStatus(allPostsTuring, contentFragment)

                allPostsTuring = [
                    ds for ds in allPostsTuring
                    if ds["id"] != integration['id']
                ]

                textContent = aem.find_all_objects(pageContent)
                spPost = {
                    'id': id,
                    't': proprieties['title'],
                    'tagLabels': '',
                    'm': " ".join(textContent),
                    'path': aem.getPathByName(contentFragment['name']),
                    'tagFragmentArea': proprieties.get('area', False),
                    'tagFragmentTheme': proprieties.get('theme', False),
                    'categoryIds': [],
                    'lastActivityAt': contentFragment['lastModified']
                }

                match integration['status']:
                    case 1:
                        turing.send(spPost, 'post')
                    case 2:
#                         turing.delete(integration['id'])
                        turing.send(spPost, 'post')

if __name__ == '__main__':
    main()
