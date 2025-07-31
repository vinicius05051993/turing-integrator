import tools.aem as aem
import tools.turing as turing
import time

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
                bannerUrl = aem.getImageUrl(proprieties.get('banner'))

                spPost = {
                    'id': id,
                    't': proprieties['title'],
                    'tagLabels': '',
                    'm': " ".join(textContent),
                    'pathFragment': aem.getPathByName(contentFragment['name']),
                    'tagFragmentArea': proprieties.get('area', False),
                    'tagFragmentTheme': proprieties.get('theme', False),
                    'categoryIds': [],
                    'lastActivityAt': int(time.time() * 1000),
                    'image': bannerUrl
                }

                match integration['status']:
                    case 1:
                        turing.send(spPost, 'post')

    for postTuring in allPostsTuring[:10]:
        turing.delete(postTuring['id'], True)

if __name__ == '__main__':
    main()
