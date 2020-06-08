from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from core.forms import DecisorForm, NomeProjetoForm, AlternativaForm, CriterioForm
from core.models import Projeto, Decisor, Alternativa, Criterio, AvaliacaoCriterios, AvaliacaoAlternativas, PageView
from .metodo import *


def index(request):
    template_name = 'index.html'
    projetos = Projeto.objects.all()

    if request.method == "POST":
        nome_projeto_form = NomeProjetoForm(request.POST)
        if nome_projeto_form.is_valid():
            projeto_novo = nome_projeto_form.save()

        return redirect('cadastradecisores', projeto_id=projeto_novo.id)

    else:
        nome_projeto_form = NomeProjetoForm()

    pageview = registra_pageview()

    return render(request, template_name, {
                'nome_projeto_form': nome_projeto_form,
                'projetos': projetos,
                'pageview': pageview})


def metodo(request):
    template_name = 'metodo.html'

    pageview = registra_pageview()

    return render(request, template_name, {
        'pageview': pageview
    })


def projeto(request, projeto_id):
    template_name = 'projeto.html'
    projeto = Projeto.objects.get(id=projeto_id)
    decisores = Decisor.objects.filter(projeto=projeto_id)
    alternativas = Alternativa.objects.filter(projeto=projeto_id)
    criterios = Criterio.objects.filter(projeto=projeto_id)


    return render(request, template_name, {
                'projeto': projeto,
                'decisores': decisores,
                'alternativas': alternativas,
                'criterios': criterios})


def deletarprojeto(request, projeto_id):
    redirect_page = '/'
    params_redirect = ''

    try:
        projeto = Projeto.objects.get(id=projeto_id)
        projeto.delete()
    except:
        redirect_page = 'resultado'
        params_redirect = projeto_id
    
    return redirect(redirect_page, projeto_id=params_redirect)


def editardados(request):
    nome = request.POST['nome']
    tipo_id = request.POST['tipoId'].split(':') 
    tipo, _id = tipo_id[0], tipo_id[1]
    
    if tipo == 'projeto':
        projeto = Projeto.objects.get(id=_id)
        projeto.nome = _nome
        projeto.save()

    elif tipo == 'decisor':
        decisor = Decisor.objects.get(id=_id)
        decisor.nome = nome
        decisor.save()

    elif tipo == 'alternativa':
        alternativa = Alternativa.objects.get(id=_id)
        alternativa.nome = nome
        alternativa.save()

    elif tipo == 'criterio':
        criterio = Criterio.objects.get(id=_id)
        criterio.nome = nome
        criterio.save()

    return HttpResponse(nome)


def cadastradecisores(request, projeto_id):
    projeto = Projeto.objects.get(id=projeto_id)
    template_name = 'cadastra_decisores.html'
    projeto_nome = projeto.nome
    decisores = Decisor.objects.filter(projeto=projeto_id)
    qtd_decisores = len(decisores)

    if request.method == 'POST':
        decisor_form = DecisorForm(request.POST)
        if decisor_form.is_valid():
            decisor_novo = decisor_form.save()
            inclui_decisor_no_projeto(projeto, decisor_novo)
            decisor_novo.projeto = projeto
            decisor_novo.save()
        return redirect('cadastradecisores', projeto_id=projeto.id)

    else:
        decisor_form = DecisorForm()

    return render(request, template_name, {
                'decisor_form': decisor_form, 
                'decisores': decisores, 
                'projeto_nome': projeto_nome,
                'projeto_id': projeto_id,
                'qtd_decisores': qtd_decisores})


def cadastraalternativas(request, projeto_id):
    projeto = Projeto.objects.get(id=projeto_id)
    template_name = 'cadastra_alternativas.html'
    projeto_nome = projeto.nome
    alternativas = Alternativa.objects.filter(projeto=projeto_id)
    ultima_alternativa = None

    if alternativas:
        ultima_alternativa = alternativas.order_by('-id')[0]

    if request.method == 'POST':
        alternativa_form = AlternativaForm(request.POST)
        if alternativa_form.is_valid():
            if ultima_alternativa:
                codigo_ultima_alternativa = ultima_alternativa.codigo
                codigo = '{}{}'.format(
                    codigo_ultima_alternativa[0],
                    int(codigo_ultima_alternativa[1])+1)
            else:
                codigo = 'a1'

            alternativa_nova = alternativa_form.save()
            alternativa_nova.projeto = projeto
            alternativa_nova.codigo = codigo
            alternativa_nova.save()
        
        return redirect('cadastraalternativas', projeto_id=projeto.id)

    else:
        alternativa_form = AlternativaForm()

    return render(request, template_name, {
                'alternativa_form': alternativa_form,
                'alternativas': alternativas,
                'projeto_nome': projeto_nome,
                'projeto_id': projeto_id})


def cadastracriterios(request, projeto_id):
    projeto = Projeto.objects.get(id=projeto_id)
    template_name = 'cadastra_criterios.html'
    projeto_nome = projeto.nome
    criterios = Criterio.objects.filter(projeto=projeto_id)
    ultimo_criterio = None

    if criterios:
        ultimo_criterio = criterios.order_by('-id')[0]

    if request.method == 'POST':
        criterio_form = CriterioForm(request.POST)
        if criterio_form.is_valid():
            if ultimo_criterio:
                codigo_ultimo_criterio = ultimo_criterio.codigo
                codigo = '{}{}'.format(
                    codigo_ultimo_criterio[0], 
                    int(codigo_ultimo_criterio[1])+1)
            else:
                codigo = 'c1'

            criterio_novo = criterio_form.save()
            criterio_novo.projeto = projeto
            criterio_novo.codigo = codigo
            criterio_novo.save()

            return redirect('cadastracriterios', projeto_id=projeto.id)
    
    else:
        criterio_form = CriterioForm()

    return render(request, template_name, {
                'criterio_form': criterio_form,
                'criterios': criterios,
                'projeto_nome': projeto_nome,
                'projeto_id': projeto_id,
    })


def avaliarcriterios(request, projeto_id):
    '''
    View para avaliar os critérios cadastrados.    
    ''' 
    template_name = 'avaliar_criterios.html'
    projeto_id = projeto_id
    projeto = Projeto.objects.get(id=projeto_id)
    decisores = list(Decisor.objects.filter(projeto=projeto_id, avaliou_criterios=False).values_list('id', 'nome'))
    criterios_cod = Criterio.objects.filter(projeto=projeto_id, numerico=False).values_list('codigo', flat=True)

    if not decisores:
        return redirect('avaliaralternativas', projeto_id)

    combinacoes_criterios = gerar_combinacoes_criterios(criterios_cod)
    
    criterios_combinados = []
    for i in combinacoes_criterios:
        cod_crit1 = i[0]
        cod_crit2 = i[1]

        nome_criterio1 = Criterio.objects.get(projeto=projeto_id, codigo=cod_crit1).nome
        nome_criterio2 = Criterio.objects.get(projeto=projeto_id, codigo=cod_crit2).nome

        criterios_combinados.append(
            (nome_criterio1, nome_criterio2, i[0], i[1])
        )

    if request.method == 'POST':
        decisor_id = request.POST['decisor_id']
        campos = request.POST.keys()
        decisor = Decisor.objects.get(id=decisor_id)

        for campo in campos:
            if campo.startswith('c') and not campo.startswith('csrf'):
                avaliacao = AvaliacaoCriterios(
                    projeto=projeto,
                    decisor=decisor,
                    criterios=campo,
                    valor=request.POST[campo]
                )
                avaliacao.save()

        decisor.avaliou_criterios = True
        decisor.save()

        return redirect('avaliarcriterios', projeto_id)

    return render(request, template_name, {
                'decisores': decisores,
                'criterios_combinados': criterios_combinados,
                'projeto_nome': projeto.nome,
                })
     

def avaliaralternativas(request, projeto_id):
    '''
    View para avaliar as alternativas cadastradas.
    '''
    template_name = 'avaliar_alternativas.html'
    projeto_id = projeto_id
    projeto = Projeto.objects.get(id=projeto_id)
    decisores = list(Decisor.objects.filter(projeto=projeto_id, avaliou_alternativas=False).values_list('id', 'nome'))
    alternativas_id = Alternativa.objects.filter(projeto=projeto_id).values_list('codigo', flat=True)
    criterios = Criterio.objects.filter(projeto=projeto_id, numerico=False)

    if not decisores:
        return redirect('resultado', projeto_id)

    combinacoes_alternativas = gerar_combinacoes_criterios(alternativas_id)

    alternativas_combinadas = []
    for i in combinacoes_alternativas:
        cod_alt1 = i[0]
        cod_alt2 = i[1]

        nome_alternativa1 = Alternativa.objects.get(projeto=projeto_id, codigo=cod_alt1).nome
        nome_alternativa2 = Alternativa.objects.get(projeto=projeto_id, codigo=cod_alt2).nome

        alternativas_combinadas.append(
            (nome_alternativa1, nome_alternativa2, i[0], i[1])
        )

    if request.method == 'POST':
        decisor_id = request.POST['decisor_id']
        campos = request.POST.keys()
        #PRINT
        print('REQUEST POSTTTTT ===>>> ',request.POST)
        decisor = Decisor.objects.get(id=decisor_id)

        for campo in campos:
            # if campo.startswith('c') and not campo.startswith('csrf'):
                # criterio_id = campo[1]
            if not campo.startswith('csrf') and not campo.startswith('d'):
                if campo.split('-->')[1].startswith('c'):
                    criterio_id = campo.split('-->')[0]

                    #### PROBLEMA ESTÁ AQUI
                    print('CAMPO',campo)
                    print('campo1', campo[1])
                    print('criterio_id', criterio_id)
                    criterio = Criterio.objects.get(id=criterio_id)
                    print('chegou aqui?')
                    avaliacao = AvaliacaoAlternativas(
                        projeto=projeto,
                        decisor=decisor,
                        criterio=criterio,
                        alternativas=campo,
                        valor=request.POST[campo],
                    )
                    avaliacao.save()
                

        decisor.avaliou_alternativas = True
        decisor.save()
        projeto.avaliado = True
        projeto.save()

        return redirect('avaliaralternativas', projeto_id)

    return render(request, template_name, {
                'decisores': decisores,
                'alternativas_combinadas': alternativas_combinadas,
                'criterios': criterios,
                'projeto_nome': projeto.nome,
                })


def resultado(request, projeto_id):
    template_name = 'resultado.html'

    projeto_id = projeto_id
    projeto = Projeto.objects.get(id=projeto_id)
    criterios = Criterio.objects.filter(projeto=projeto_id, numerico=False)
    qtd_criterios = criterios.count()
    qtd_alternativas = Alternativa.objects.filter(projeto=projeto_id).count()
    decisores = projeto.decisores.all()

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

        matriz = gerar_matriz(qtd_criterios, criterios_decisor)
        matrizes.append(matriz)

    # calcular pesos dos decisores
    pesos_decisores = []
    for matriz in matrizes:
        print('>>>>>>>>>>>>>>>')
        print('matriz =>', matriz)
        print('>>>>>>>>>>>>>>>')

        peso_matriz = normalizar(matriz)
        pesos_decisores.append(peso_matriz)

    # calcular o peso final 
    peso_final = peso_criterios(pesos_decisores)

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
            matriz = gerar_matriz_alt(qtd_alternativas, matriz_base_alt, lista_avaliacao)
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
            s = normalizar_alternativas(v[idx])
            avaliacoes_alternativas[idx].append(s)
        idx += 1
        count += 1

    lista_somas = []
    for lista_elementos in avaliacoes_alternativas:
        soma = soma_alternativa_por_criterio(lista_elementos)
        lista_somas.append(soma)

    resultado_um = multiplica_final(lista_somas, peso_final)

    alternativas = Alternativa.objects.filter(projeto=projeto_id)

    resultado = []
    count = 0

    while count < len(alternativas):
        resultado.append( 
            (alternativas[count], resultado_um[count]) 
        )
        count += 1

    resultado.sort(key=lambda x: x[1] ,reverse=True)


    return render(request, template_name, {
        'projeto_nome': projeto.nome,
        'projeto_id': projeto.id,
        'resultado': resultado,
        'pesos_criterios': pesos_criterios,
        })


#################################
######## aux functions   ########
#################################
# TODO: colocar em arquivo separado

