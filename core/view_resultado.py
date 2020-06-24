
    projeto_id = projeto_id
    projeto = Projeto.objects.get(id=projeto_id)
    qtd_criterios = Criterio.objects.filter(projeto=projeto_id).count()
    qtd_alternativas = Alternativa.objects.filter(projeto=projeto_id).count()
    decisores = projeto.decisores.all()
    criterios = Criterio.objects.filter(projeto=projeto_id)

    #### Criterios ####
    matrizes = []
    for decisor in decisores:
        criterios_decisor = AvaliacaoCriterios.objects.filter(projeto=projeto_id, decisor=decisor.id)

        # print('XXXXXXXXXXXXXXXXXXXXXXXXXX')
        # print('decisor =>', decisor.nome)
        # print('criterios_decisor =>', criterios_decisor)
        # print('criterios_decisor VALOR =>', criterios_decisor[0].valor)
        # print('qtd_criterios =>', qtd_criterios)
        # print('XXXXXXXXXXXXXXXXXXXXXXXXXX')

        matriz = _gerar_matriz(qtd_criterios, criterios_decisor)
        matrizes.append(matriz)

    # calcular pesos dos decisores
    pesos_decisores = []
    for matriz in matrizes:
        print('>>>>>>>>>>>>>>>')
        print('matriz =>', matriz)
        print('>>>>>>>>>>>>>>>')

        peso_matriz = _normalizar(matriz)
        pesos_decisores.append(peso_matriz)

    # calcular o peso final
    peso_final = _peso_criterios(pesos_decisores)

    # cria tupla de criterio e peso para renderizar
    pesos_criterios = []
    pos_peso = 0
    peso_final_qt = len(peso_final)

    while pos_peso < peso_final_qt:
        for criterio in criterios:
            pesos_criterios.append((criterio.nome, peso_final[pos_peso]))
            pos_peso += 1

    #### Alternativas ####
    # gera dicionario de matrizes
    d_matrizes = {}
    for decisor in decisores:
        k = 'D{}'.format(decisor.id)
        d_matrizes[k] = []

    # gera dicionario de avaliacoes
    d_avaliacoes = {}
    for decisor in decisores:
        k = 'D{}'.format(decisor.id)
        d_avaliacoes[k] = []
        for i in range(qtd_criterios):
            d_avaliacoes[k].append(list())

    lista_criterios = []
    for c in criterios:
        lista_criterios.append(c.codigo)

    avaliacoes_alt = AvaliacaoAlternativas.objects.filter(projeto=projeto_id).order_by('alternativas')

    for i in avaliacoes_alt:
        k = 'D{}'.format(i.decisor.id)
        indice = lista_criterios.index(i.criterio.codigo)
        d_avaliacoes[k][indice].append(i.valor)


    # gera matrizes
    for k,v in d_avaliacoes.items():
        for idx, val in enumerate(v):
            matriz_base_alt = []
            for i in range(qtd_alternativas):
                matriz_base_alt.append(list(range(1,qtd_alternativas+1)))

            lista_avaliacao = val
            matriz = _gerar_matriz_alt(qtd_alternativas, matriz_base_alt, lista_avaliacao)
            d_matrizes[k].append(matriz)


    # soma alternativas por criterio
    avaliacoes_alternativas = []
    for i in range(qtd_criterios):
        avaliacoes_alternativas.append(list())

    count = 1
    idx = 0

    # while count <= qtd_alternativas:
    while count <= qtd_criterios:
        for k, v in d_matrizes.items():
            s = _normalizar_alternativas(v[idx])
            avaliacoes_alternativas[idx].append(s)
        idx += 1
        count += 1

    lista_somas = []
    for lista_elementos in avaliacoes_alternativas:
        soma = _soma_alternativa_por_criterio(lista_elementos)
        lista_somas.append(soma)

    resultado_um = _multiplica_final(lista_somas, peso_final)

    alternativas = Alternativa.objects.filter(projeto=projeto_id)

    resultado = []
    count = 0

    while count < len(alternativas):
        resultado.append(
            (alternativas[count], resultado_um[count])
        )
        count += 1

    resultado.sort(key=lambda x: x[1] ,reverse=True)
