import tools.aem as aem

def main():
    allPosts = aem.getAllPosts()

    for post in allPosts:
        pageContent = aem.getPageOfPost(post)
        if pageContent:
            results = aem.find_all_objects(pageContent)
            print(results)
            break

if __name__ == '__main__':
    main()
