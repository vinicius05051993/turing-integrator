import tools.aem as aem
import tools.turing as turing
import time
from dateutil import parser
import datetime

def main():
    allContentFragment = aem.getAllContentFragment()
    allPostsTuring =  turing.getAllTuringIds('post')
    allEventsTuring =  turing.getAllTuringIds('event')

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
                    'publicationDate': dt.isoformat(),
                    'image': proprieties.get('banner', ''),
                    'highlights': proprieties.get('highlights', False)
                }

                match integration['status']:
                    case 1:
                        turing.send(spPost, 'post')

        if aem.isEvent(id):
            proprieties = aem.getContentFragmentProprieties(id)
            originProprieties = aem.getOriginProprieties(id)
            if proprieties:
                dt = datetime.datetime.strptime(contentFragment['lastModified'], "%Y-%m-%d %H:%M:%S")
                contentFragment['lastModified'] = int(dt.timestamp() * 1000)

                integration = aem.integrationStatus(allEventsTuring, contentFragment)

                allEventsTuring = [
                    ds for ds in allEventsTuring
                    if ds["id"] != integration['id']
                ]

                dt = parser.parse(originProprieties.get('jcr:created'))

                spPost = {
                    'id': id,
                    't': proprieties['title'],
                    'tagLabels': '',
                    'pathFragment': aem.getPathByName(contentFragment['name'], 'events'),
                    'tagFragmentArea': [],
                    'tagFragmentTheme': [],
                    'categoryIds': [],
                    'lastActivityAt': contentFragment['lastModified'],
                    'publicationDate': dt.isoformat(),
                    'image': '',
                    'highlights': False,
                    'buttonTextFragment': proprieties.get('buttonText', 'Acesse aqui'),
                    'descriptionFragment': proprieties.get('description', ''),
                    'eventType': proprieties.get('eventType', []),
                    'initialDate': proprieties.get('initialDate', ''),
                    'allDay': proprieties.get('allDay', False) == 'true',
                    'buttonLink': proprieties.get('buttonLink', ''),
                    'finishDate': proprieties.get('finishDate', '')
                }

                spPost['m'] = spPost['descriptionFragment']
                + ' - link para acessar evento: ' + spPost['buttonLink']
                + ' - Data Inicial: ' + spPost['initialDate']
                + ' - Data Final: ' + spPost['finishDate']

                if spPost['allDay']:
                    spPost['m'] += ' - Evento o dia todo'

                match integration['status']:
                    case 1:
                        turing.send(spPost, 'event')

    for postTuring in allPostsTuring[:100]:
        turing.delete(postTuring['id'], True)

    for eventTuring in allEventsTuring[:100]:
        turing.delete(eventTuring['id'], False)

if __name__ == '__main__':
    main()
