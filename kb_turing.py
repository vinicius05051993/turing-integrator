import tools.turing as turing
import tools.kb as kb

def main():

    allManualsTuring = turing.getAllTuringIds('manual')

    kbPosts = kb.getPosts()

    for kbPost in kbPosts:
        integration = turing.integrationStatus(allManualsTuring, kbPost)

        allManualsTuring = [
            ds for ds in allManualsTuring
            if ds["id"] != integration['id']
        ]

        match integration['status']:
            case 1:
                kbPost = kb.getPostDetails(kbPost)
                turing.kbSend(kbPost)

    for manualTuringToDelete in allManualsTuring[:1]:
        turing.delete(manualTuringToDelete['id'], True)
        

if __name__ == '__main__':
    main()