import pandas as pd
from .metodo import DecisionMatrix
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from core.forms import DecisorForm, NomeProjetoForm, AlternativaForm, CriterioForm
from core.models import Projeto, Decisor, Alternativa, Criterio, AvaliacaoCriterios, AvaliacaoAlternativas, PageView
from itertools import combinations


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
            # _inclui_decisor_no_projeto(projeto, decisor_novo)
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

    if request.method == 'POST':
        alternativa_form = AlternativaForm(request.POST)
        if alternativa_form.is_valid():
            alternativa_nova = alternativa_form.save()
            alternativa_nova.projeto = projeto
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

    if request.method == 'POST':
        criterio_form = CriterioForm(request.POST)
        if criterio_form.is_valid():
            criterio_novo = criterio_form.save()
            criterio_novo.projeto = projeto
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
    decisores = Decisor.objects.filter(projeto=projeto_id)
    criterios = Criterio.objects.filter(projeto=projeto_id)

    criterios_combinados = list(combinations(criterios, 2))

    if request.method == 'POST':
        requisicao = dict(request.POST)
        _ = requisicao.pop('decisor_id')
        _ = requisicao.pop('csrfmiddlewaretoken')
        decisor_id = request.POST['decisor_id']
        campos = requisicao
        decisor = Decisor.objects.get(id=decisor_id)

        frame = {x: int(y[0]) for x,y  in campos.items()}

        frame = DecisionMatrix(frame).matrix.to_dict()
        print(frame)

        avaliacao = AvaliacaoCriterios(
            projeto=projeto,
            decisor=decisor,
            avaliacao=frame
        )
        avaliacao.save()

        # decisor.save()

        return redirect('avaliaralternativas', projeto_id)

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
    projeto_id=7
    projeto_id = projeto_id
    projeto = Projeto.objects.get(id=projeto_id)
    decisores = Decisor.objects.filter(projeto=projeto_id)
    alternativas = Alternativa.objects.filter(projeto=projeto_id)
    criterios = Criterio.objects.filter(projeto=projeto_id)

    alternativas_combinadas = list(combinations(alternativas, 2))


    if request.method == 'POST':
        requisicao = dict(request.POST)
        _ = requisicao.pop('csrfmiddlewaretoken')
        decisor_id = request.POST['decisor_id']
        campos = requisicao
        decisor = Decisor.objects.get(id=decisor_id)

        df = pd.DataFrame.from_dict(requisicao)
        print(df)

        for decisor in set(requisicao['decisor_id']):
            for criterio in set(requisicao['criterio_id']):
                filtro = (df['decisor_id'] == decisor) & (df['criterio_id'] == criterio)
                df2 = df[filtro].drop(columns=['decisor_id', 'criterio_id'])
                valor = int(df2.values.tolist()[0][0])
                # frame = {x: int(y[0]) for x,y  in .items()}

        return redirect('avaliaralternativas', projeto_id)

    return render(request, template_name, {
                'decisores': decisores,
                'alternativas_combinadas': alternativas_combinadas,
                'criterios': criterios,
                'projeto_nome': projeto.nome,
                })


def resultado(request, projeto_id):
    avaliacoes = AvaliacaoCriterios.object.filter(projeto_id=projeto_id)

    template_name = 'resultado.html'

    dataframes = [pd.DataFrame.from_dict(aval.avaliacao).to_html() for aval in avaliacoes]

    return render(request, template_name, {
        # 'projeto_nome': projeto.nome,
        # 'projeto_id': projeto.id,
        # 'resultado': resultado,
        # 'pesos_criterios': pesos_criterios,
        'dataframes': dataframes
        })


def registra_pageview():
    pageviews = PageView.objects.all()

    if pageviews:
        pageview = pageviews.get(id=1)
        pageview.views += 1
    else:
        pageview = PageView()
        pageview.views = 1
    pageview.save()

    return pageview.views
