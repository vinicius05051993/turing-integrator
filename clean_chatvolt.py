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
            # Mantém o primeiro e marca os outros para exclusão
            ids_para_excluir.extend(ids[1:])

    print(ids_para_excluir)

if __name__ == '__main__':
    main()
