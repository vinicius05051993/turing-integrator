import tools.aem as aem

def main():
    allPosts = aem.getAllPosts()

    for post in allPosts:
        html = aem.getHtmlOfPost(post)
        print(aem.get_only_texts(html))

if __name__ == '__main__':
    main()
