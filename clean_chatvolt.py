import tools.chatvolt as chatvolt
from collections import Counter

def main():
    chatVoltDatas = chatvolt.getAll()
    chatVoltDataSources = chatVoltDatas.get("datasources", {})

    ids = [chatVoltData['id'] for chatVoltData in chatVoltDataSources]
    contagem = Counter(ids)

    resultado = [(id_, qtd) for id_, qtd in contagem.items() if qtd > 1]

    print(resultado)

if __name__ == '__main__':
    main()