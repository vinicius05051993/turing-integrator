import tools.aem as aem
import tools.turing as turing
import time
from datetime import datetime, timezone

def main():
    allContentFragment = aem.getAllContentFragment()
    allPostsTuring =  turing.getAllTuringIds('post')

    for contentFragment in allContentFragment:
        id = contentFragment['path']
        if aem.isPost(id):
            proprieties = aem.getContentFragmentProprieties(id)
            pageContent = aem.getPageContent(id)
            if proprieties and pageContent:
                contentFragment['lastModified'] = pageContent['lastModifiedDate']
                integration = aem.integrationStatus(allPostsTuring, contentFragment)

                allPostsTuring = [
                    ds for ds in allPostsTuring
                    if ds["id"] != integration['id']
                ]

                textContent = aem.find_all_objects(pageContent)
                lastActivityAt = datetime.fromtimestamp(contentFragment["lastModified"] / 1000, tz=timezone.utc)

                spPost = {
                    'id': id,
                    't': proprieties['title'],
                    'tagLabels': '',
                    'm': " ".join(textContent),
                    'pathFragment': aem.getPathByName(contentFragment['name']),
                    'tagFragmentArea': proprieties.get('area', False),
                    'tagFragmentTheme': proprieties.get('theme', False),
                    'categoryIds': [],
                    'lastActivityAt': lastActivityAt,
                    'image': proprieties.get('banner', '')
                }

                match integration['status']:
                    case 1:
                        turing.send(spPost, 'post')

    for postTuring in allPostsTuring[:10]:
        turing.delete(postTuring['id'], True)

if __name__ == '__main__':
    main()
