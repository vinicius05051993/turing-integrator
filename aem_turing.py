import tools.aem as aem

def main():
    allPosts = aem.getAllPosts()

    for post in allPosts:
        pageContent = aem.getHtmlOfPost(post)
        if pageContent:
            print(pageContent)
            break

if __name__ == '__main__':
    main()
