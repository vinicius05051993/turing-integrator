import tools.aem as aem
import tools.turing as turing
import time
from dateutil import parser

def main():
    allContentFragment = aem.getAllContentFragment()
    allPostsTuring =  turing.getAllTuringIds('post')

    for contentFragment in allContentFragment:
        id = contentFragment['path']
        if aem.isPost(id):
            proprieties = aem.getContentFragmentProprieties(id)
            pageContent = aem.getPageContent(id)
            originProprieties = aem.getOriginProprieties(id)
            if proprieties and pageContent:
                contentFragment['lastModified'] = pageContent['lastModifiedDate']
                integration = aem.integrationStatus(allPostsTuring, contentFragment)

                allPostsTuring = [
                    ds for ds in allPostsTuring
                    if ds["id"] != integration['id']
                ]

                textContent = aem.find_all_objects(pageContent)

                dt = parser.parse(originProprieties.get('jcr:created'))

                spPost = {
                    'id': id,
                    't': proprieties['title'],
                    'tagLabels': '',
                    'm': " - ".join(textContent),
                    'pathFragment': aem.getPathByName(contentFragment['name']),
                    'tagFragmentArea': proprieties.get('area', False),
                    'tagFragmentTheme': proprieties.get('theme', False),
                    'categoryIds': [],
                    'lastActivityAt': contentFragment['lastModified'],
                    'publicationDate': int(dt.timestamp() * 1000),
                    'image': proprieties.get('banner', ''),
                    'highlights': proprieties.get('highlights', False)
                }

                match integration['status']:
                    case 1:
                        turing.send(spPost, 'post')

    for postTuring in allPostsTuring[:100]:
        turing.delete(postTuring['id'], True)

if __name__ == '__main__':
    main()
