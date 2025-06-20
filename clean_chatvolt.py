import tools.chatvolt as chatvolt
from collections import Counter, defaultdict

def main():
    chatVoltDatas = chatvolt.getAll()
    chatVoltDataSources = chatVoltDatas.get("datasources", {})

    # Agrupa todos os itens por nome
    nomes_agrupados = defaultdict(list)
    for item in chatVoltDataSources:
        nomes_agrupados[item['name']].append(item['id'])

    # Pega apenas os nomes repetidos e seus respectivos IDs
    ids_para_excluir = []
    for nome, ids in nomes_agrupados.items():
        if len(ids) > 1:
            ids_para_excluir.extend(ids[1:])

    print(ids_para_excluir)

    for id in ids_para_excluir:
        chatvolt.delete(id)

if __name__ == '__main__':
    main()
