import tools.aem as aem
import tools.turing as turing
import time
from dateutil import parser
import datetime

def main():
    params = {
        "path": "/content/maple-bear/posts",
        "type": "cq:Page",
        "property": "jcr:content/cq:lastReplicationAction",
        "property.value": "Activate",
        "p.limit": "-1",
        "orderby": "path"
    }

    allContentFragment = aem.getAllContentFragment(params)
    allPostsTuring =  turing.getAllTuringIds('post')

    for contentFragment in allContentFragment:
        id = contentFragment['path']
        if aem.isPost(id) and False:
            proprieties = aem.getContentFragmentProprieties(id, params)
            pageContent = aem.getPageContent(id)
            originProprieties = aem.getOriginProprieties(id, params)
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


    params = {
        "type": "dam:Asset",
        "property": "jcr:content/cq:lastReplicationAction",
        "property.value": "Activate",
        "p.limit": "-1",
        "orderby": "path"
    }

    allContentFragment = aem.getAllContentFragment(params)
    allEventsTuring =  turing.getAllTuringIds('event')

    for contentFragment in allContentFragment:
        id = contentFragment['path']
        if aem.isEvent(id):
            proprieties = aem.getContentFragmentProprieties(id, params)
            originProprieties = aem.getOriginProprieties(id, params)
            if proprieties and proprieties.get('title'):
                dt = datetime.datetime.strptime(contentFragment.get('lastModified', '2020-01-01 17:28:58'), "%Y-%m-%d %H:%M:%S")
                contentFragment['lastModified'] = int(dt.timestamp() * 1000)

                integration = aem.integrationStatus(allEventsTuring, contentFragment)

                allEventsTuring = [
                    ds for ds in allEventsTuring
                    if ds["id"] != integration['id']
                ]

                dt = parser.parse(originProprieties.get('jcr:created'))

                spPost = {
                    'id': id,
                    't': proprieties.get('title'),
                    'tagLabels': '',
                    'm': '',
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

                spPost['m'] = str(proprieties.get('description', ''))
                spPost['m'] += '. link para acessar evento: ' + str(proprieties.get('buttonLink', ''))

                # Obtém e formata a data inicial
                initial_date_str = proprieties.get('initialDate', '')
                try:
                    initial_date_fmt = parser.parse(initial_date_str).strftime('%d/%m/%Y %H:%M:%S') if initial_date_str else ''
                except Exception:
                    initial_date_fmt = initial_date_str

                # Obtém e formata a data final
                finish_date_str = proprieties.get('finishDate', '')
                try:
                    finish_date_fmt = parser.parse(finish_date_str).strftime('%d/%m/%Y %H:%M:%S') if finish_date_str else ''
                except Exception:
                    finish_date_fmt = finish_date_str

                spPost['m'] += '. Data Inicial: ' + initial_date_fmt
                spPost['m'] += '. Data Final: ' + finish_date_fmt

                if spPost['allDay']:
                    spPost['m'] += '. Evento o dia todo'

                match integration['status']:
                    case 1:
                        print(spPost)
                        turing.send(spPost, 'event')

#     for postTuring in allPostsTuring[:100]:
#         turing.delete(postTuring['id'], True)
#
#     for eventTuring in allEventsTuring[:100]:
#         turing.delete(eventTuring['id'], False)

if __name__ == '__main__':
    main()
