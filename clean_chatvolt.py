import tools.chatvolt as chatvolt
from collections import Counter, defaultdict

def main():
    chatVoltDatas = chatvolt.getAll()
    chatVoltDataSources = chatVoltDatas.get("datasources", {})

    nomes_agrupados = defaultdict(list)
    for item in chatVoltDataSources:
        if "maplebear.activehosted.com" not in item['name']:
            nomes_agrupados[item['name']].append(item['id'])

    ids_para_excluir = []
    for nome, ids in nomes_agrupados.items():
        if len(ids) > 1:
            ids_para_excluir.extend(ids[1:])

    for id in ids_para_excluir:
        chatvolt.delete(id)

if __name__ == '__main__':
    main()
