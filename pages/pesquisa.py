import dash
from dash import html, dcc, callback, Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

dash.register_page(__name__)

df = pd.read_csv('user_answers2022-2023teste.csv')

projetos_upe = df.groupby('UNIDADE')['Coordenação de projeto de pesquisa, de desenvolvimento ou de inovação cadastrado no SISPG COM auxílio financeiro da UPE.'].sum()

projetos_externos = df.groupby('UNIDADE')['Coordenação de projeto de pesquisa, de desenvolvimento ou de inovação cadastrado no SISPG COM auxílio financeiro externo à UPE.'].sum()

projetos_sem_apoio = df.groupby('UNIDADE')['Coordenação de projeto de pesquisa, de desenvolvimento ou de inovação, na UPE, cadastrado no SISPG e aprovado pela Unidade SEM auxílio financeiro.'].sum()

df_projetos = pd.DataFrame({
    'Projetos UPE': projetos_upe,
    'Projetos Externos': projetos_externos,
    'Projetos Sem Apoio': projetos_sem_apoio
})

df_projetos = df_projetos.sort_values(by=['Projetos UPE', 'Projetos Externos', 'Projetos Sem Apoio'], ascending=False)

projetos_por_financ_bargraph = go.Figure(data=[
    go.Bar(name='Projetos UPE', x=df_projetos.index, y=df_projetos['Projetos UPE'], marker_color='#88c425', text=df_projetos['Projetos UPE'], textposition='outside'),
    go.Bar(name='Projetos Externos', x=df_projetos.index, y=df_projetos['Projetos Externos'], marker_color='#1b676b', text=df_projetos['Projetos Externos'], textposition='outside'),
    go.Bar(name='Projetos Sem Apoio', x=df_projetos.index, y=df_projetos['Projetos Sem Apoio'], marker_color='#6f0b00', text=df_projetos['Projetos Sem Apoio'], textposition='outside')
])

# Personalização do gráfico
projetos_por_financ_bargraph.update_layout(
    title=dict(
            text='Número de Projetos por Tipo de Apoio Financeiro e Unidade',
            y=0.85,
            xanchor='left',
            font=dict(
                size=20,
                color='black',
                weight='bold'
            ),
        ),
    xaxis_title='Unidade',
    xaxis_title_font_size=12,
    yaxis_title='Número de Projetos',
    yaxis_title_font_size=12,
    barmode='group',
)

# Ajusta a posição do texto para cada barra
for i, trace in enumerate(projetos_por_financ_bargraph.data):
    projetos_por_financ_bargraph.data[i].textposition = 'outside'
    projetos_por_financ_bargraph.data[i].text = [f'{int(value)}' for value in trace.y]

lideres_pesquisa = df.groupby('UNIDADE')['Líder de grupo de pesquisa cadastrado no CNPq e certificado pela UPE'].sum()
lideres_pesquisa = lideres_pesquisa.sort_values(ascending=False)

lideres_pesquisa_bargraph = go.Figure(data=[go.Bar(
    y=lideres_pesquisa.index,
    x=lideres_pesquisa.values,
    orientation='h',
    marker_color='#1b676b',
    text=[f'{int(valor)}' for valor in lideres_pesquisa.values],
    textposition='inside',
    textangle=0
)])

# Personalização do gráfico
lideres_pesquisa_bargraph.update_layout(
    title=dict(
            text='Quantidade de Professores Líderes de Pesquisa por Unidade',
            y=0.85,
            xanchor='left',
            font=dict(
                size=20,
                color='black',
                weight='bold'
            ),
        ),
    xaxis_title='Número de Professores Líderes de Pesquisa',
    xaxis_title_font_size=14,
    yaxis_title='Unidade',
    yaxis_title_font_size=12,
)

layout = html.Main([
            html.H2(id='', className='mainpage__subtitle', children='Pesquisa científica'),
            dcc.Graph(figure=projetos_por_financ_bargraph),
            html.P(children='Tipo de artigo: ', className='body__text'),
            dcc.RadioItems(['Científico', 'Extensão'], 'Científico', inline=True, id='radio__selection-bargrapharticle', className='body__text'),
            dcc.Graph(id='bargrapharticle'),
            dcc.Graph(figure=lideres_pesquisa_bargraph),
        ])

@callback(
    Output('bargrapharticle', 'figure'),
    Input('radio__selection-bargrapharticle', 'value')
)
def update_graph(value):
    if value == 'Científico':
        colunas_publicacoes_a = [
            'Publicação de artigo científico em periódico indexado - qualis A1',
            'Publicação de artigo científico em periódico indexado - qualis A2',
            'Publicação de artigo científico em periódico indexado - qualis A3',
            'Publicação de artigo científico em periódico indexado - qualis A4',
        ]

        colunas_publicacoes_b = [
            'Publicação de artigo científico em periódico indexado - qualis B1',
            'Publicação de artigo científico em periódico indexado - qualis B2',
            'Publicação de artigo científico em periódico indexado - qualis B3',
            'Publicação de artigo científico em periódico indexado - qualis B4',
            'Publicação de artigo científico em periódico indexado - sem qualis'
        ]
        soma_publicacoes_a_por_unidade = df.groupby('UNIDADE')[colunas_publicacoes_a].sum()
        soma_publicacoes_b_por_unidade = df.groupby('UNIDADE')[colunas_publicacoes_b].sum()

        # Criando uma nova coluna com a soma total de publicações qualis A
        soma_publicacoes_a_por_unidade['Soma total de publicações qualis A'] = soma_publicacoes_a_por_unidade.sum(axis=1)

        # Criando uma nova coluna com a soma total de publicações qualis B e sem qualis
        soma_publicacoes_b_por_unidade['Soma total de publicações qualis B e sem qualis'] = soma_publicacoes_b_por_unidade.sum(axis=1)

        # Combinando as duas somas em um único DataFrame
        resultado_final = pd.DataFrame({
            'UNIDADE': soma_publicacoes_a_por_unidade.index,
            'Soma total de publicações qualis A': soma_publicacoes_a_por_unidade['Soma total de publicações qualis A'],
            'Soma total de publicações qualis B e sem qualis': soma_publicacoes_b_por_unidade['Soma total de publicações qualis B e sem qualis']
        })

        fig = px.bar(resultado_final, y="UNIDADE", x=["Soma total de publicações qualis A", "Soma total de publicações qualis B e sem qualis"], orientation="h")
        
        fig.update_layout(
            title=dict(
            text='Soma de publicações por unidade',
            y=0.93,
            xanchor='left',
            font=dict(
                size=20,
                color='black',
                weight='bold'
            ),
            ),
        )
        return fig
    
    elif value == 'Extensão':
        colunas_publicacoes_a = [
            'Publicação de artigo de extensão em periódico indexado - qualis A1.',
            'Publicação de artigo de extensão em periódico indexado - qualis A2',
            'Publicação de artigo de extensão em periódico indexado - qualis A3',
            'Publicação de artigo de extensão em periódico indexado - qualis A4',
        ]

        colunas_publicacoes_b = [
            'Publicação de artigo de extensão em periódico indexado - qualis B1',
            'Publicação de artigo de extensão em periódico indexado - qualis B2',
            'Publicação de artigo de extensão em periódico indexado - qualis B3',
            'Publicação de artigo de extensão em periódico indexado - qualis B4',
            'Publicação de artigo de extensão em periódico indexado - sem qualis'
        ]
        soma_publicacoes_a_por_unidade = df.groupby('UNIDADE')[colunas_publicacoes_a].sum()
        soma_publicacoes_b_por_unidade = df.groupby('UNIDADE')[colunas_publicacoes_b].sum()

        # Criando uma nova coluna com a soma total de publicações qualis A
        soma_publicacoes_a_por_unidade['Soma total de publicações qualis A'] = soma_publicacoes_a_por_unidade.sum(axis=1)

        # Criando uma nova coluna com a soma total de publicações qualis B e sem qualis
        soma_publicacoes_b_por_unidade['Soma total de publicações qualis B e sem qualis'] = soma_publicacoes_b_por_unidade.sum(axis=1)

        # Combinando as duas somas em um único DataFrame
        resultado_final = pd.DataFrame({
            'UNIDADE': soma_publicacoes_a_por_unidade.index,
            'Soma total de publicações qualis A': soma_publicacoes_a_por_unidade['Soma total de publicações qualis A'],
            'Soma total de publicações qualis B e sem qualis': soma_publicacoes_b_por_unidade['Soma total de publicações qualis B e sem qualis']
        })

        fig = px.bar(resultado_final, y="UNIDADE", x=["Soma total de publicações qualis A", "Soma total de publicações qualis B e sem qualis"], orientation="h")

        fig.update_layout(
            title=dict(
            text='Soma de publicações por unidade',
            y=0.93,
            xanchor='left',
            font=dict(
                size=20,
                color='black',
                weight='bold'
            ),
            ),
        )
        return fig