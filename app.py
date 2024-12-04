from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# df = pd.read_csv('user_answers2022-2023.csv')
df = pd.read_csv('user_answers2022-2023teste.csv')

units = sorted(df['UNIDADE'].unique())

#################
## Violin Plot ##
#################

colunas_numericas = [
    'Carga_Horaria_Semanal',
    'Carga horária semanal na graduação, exclusivamente na modalidade EAD na UPE, em atividade de ensino com aulas desenvolvidas em disciplina, componente curricular ou módulo.',
    'Carga horária semanal na pós-graduação stricto sensu, presencial ou EAD, na UPE, em atividade de ensino com aulas desenvolvidas em disciplina, componente curricular ou módulo.',
    'Carga horária semanal em cursos de especialização lato sensu DENTRO da carga horária contratual, incluindo a modalidade EAD e/ou programas de residência na UPE, em atividade de ensino com aulas desenvolvidas em disciplina, componente curricular ou módulo.'
]

df[colunas_numericas] = df[colunas_numericas].apply(pd.to_numeric, errors='coerce')

df['Soma carga horária'] = df[colunas_numericas].sum(axis=1)

dataset_violin = df[['DOCENTE', 'UNIDADE', 'Soma carga horária']]

violin = go.Figure()
for unity_name in units:
    violin.add_trace(go.Violin(x=df['UNIDADE'][df['UNIDADE'] == unity_name],
                                y=dataset_violin['Soma carga horária'][dataset_violin['UNIDADE'] == unity_name],
                                name=unity_name,
                                meanline_visible=True,
                                fillcolor='rgba(166, 58, 80, 0.7)',
                                line_color='rgba(166, 58, 80, 1)',
                                showlegend=False,
                                hoverinfo='y+name'
                            ))
violin.update_layout(title_text="Carga horária semanal na graduação, pós-graduação e cursos lato sensu, presencial ou EAD, por unidade")

####################################################
## Orientações concluidas e em andamento Bar Plot ##
####################################################

orientacoes_andamento = df.groupby('UNIDADE')[['Orientacao_Andamento_Mestrado', 'Orientacao_Andamento_Doutorado', 'Orientacao_Concluida_Mestrado', 'Orientacao_Concluida_Doutorado']].sum()
orientacoes_andamento['Total_Orientacoes_Andamento'] = orientacoes_andamento['Orientacao_Andamento_Mestrado'] + orientacoes_andamento['Orientacao_Andamento_Doutorado'] + orientacoes_andamento['Orientacao_Concluida_Mestrado'] + orientacoes_andamento['Orientacao_Concluida_Doutorado']

professores_por_unidade = df['UNIDADE'].value_counts()
media_orientacoes_andamento = orientacoes_andamento['Total_Orientacoes_Andamento'] / professores_por_unidade

media_orientacoes_andamento = media_orientacoes_andamento.reset_index().rename(columns={'index': 'UNIDADE', 0: 'Media_Orientacoes_Andamento'})

media_pos_bargraph = go.Figure(data=[go.Bar(
    y=media_orientacoes_andamento['UNIDADE'],
    x=media_orientacoes_andamento['Media_Orientacoes_Andamento'],
    orientation='h',
    marker_color='#1b676b',
    text=[f'{round(valor, 2)}' for valor in media_orientacoes_andamento['Media_Orientacoes_Andamento']],
)])

media_pos_bargraph.update_layout(
    title='Orientações concluídas e em andamento por Docente - Pós-graduação',
    xaxis_title='Orientações em andamento por docente',
    yaxis_title='Unidade',
    # font=dict(
    #     size=14,  # Set the font size here
    # )
)

media_pos_bargraph.update_traces(textposition='inside', textfont_size=18)

#####################################################
## Número de projetos por tipo de apoio financeiro ##
#####################################################

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
    title='Número de Projetos por Tipo de Apoio Financeiro e Unidade',
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

###############################################################
## Quantidade de professores líderes de pesquisa por unidade ##
###############################################################

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
    title='Quantidade de Professores Líderes de Pesquisa por Unidade',
    xaxis_title='Número de Professores Líderes de Pesquisa',
    xaxis_title_font_size=14,
    yaxis_title='Unidade',
    yaxis_title_font_size=12,
)

app = Dash()

app.layout = [
    html.H1(children='Relatório de Atividades Docentes (RAD) 2023 - Tópicos Avançados em Sistemas de Informação II', className='mainpage__title'),
    html.H2(id='', className='mainpage__subtitle', children='Carga horária docente'),
    html.P(children='Métrica utilizada: '),
    dcc.RadioItems(['Média', 'Mediana'], 'Média', inline=True, id='radio__selection-lollipop'),
    dcc.Graph(id='lollipop-graph'),
    dcc.Graph(figure=violin),
    html.H2(id='', className='mainpage__subtitle', children='Orientações de trabalhos'),
    html.P(children='Cor dos professores: '),
    dcc.RadioItems(['Docente de pós graduação', 'Docente participa de laboratórios de pesquisa'], 'Docente de pós graduação', inline=True, id='radio__selection-beeswarm'),
    dcc.Graph(id='beeswarm-graph'),
    dcc.Graph(figure=media_pos_bargraph),
    html.H2(id='', className='mainpage__subtitle', children='Pesquisa científica'),
    dcc.Graph(figure=projetos_por_financ_bargraph),
    html.P(children='Tipo de artigo: '),
    dcc.RadioItems(['Científico', 'Extensão'], 'Científico', inline=True, id='radio__selection-bargrapharticle'),
    dcc.Graph(id='bargrapharticle'),
    dcc.Graph(figure=lideres_pesquisa_bargraph),
]

@callback(
    Output('lollipop-graph', 'figure'),
    Input('radio__selection-lollipop', 'value')
)
def update_graph(value):
    df_filtered = df[df['STATUS'] != 'Pendente']

    min_carga_horaria = df_filtered.groupby('UNIDADE')['Carga_Horaria_Semanal'].min()
    max_carga_horaria = df_filtered.groupby('UNIDADE')['Carga_Horaria_Semanal'].max()
    media_carga_horaria = df_filtered.groupby('UNIDADE')['Carga_Horaria_Semanal'].mean()
    mediana_carga_horaria = df_filtered.groupby('UNIDADE')['Carga_Horaria_Semanal'].median()
    
    # Unir os dados mínimos e máximos em um DataFrame
    carga_horaria_unidade = pd.DataFrame({
        'Carga_Horaria_Minima': min_carga_horaria,
        'Carga_Horaria_Maxima': max_carga_horaria,
        'Carga_Horaria_Media': media_carga_horaria,
        'Carga_Horaria_Mediana': mediana_carga_horaria
    }).reset_index()

    # Preparar os dados para as linhas de conexão
    line_x = []
    line_y = []

    for _, row in carga_horaria_unidade.iterrows():
        line_x.extend([row['Carga_Horaria_Minima'], row['Carga_Horaria_Maxima'], None])
        line_y.extend([row['UNIDADE'], row['UNIDADE'], None])

    fig_data = [
        go.Scatter(
            x=line_x,
            y=line_y,
            mode="lines",
            showlegend=False,
            marker=dict(color="grey")
        ),
        go.Scatter(
            x=carga_horaria_unidade['Carga_Horaria_Minima'],
            y=carga_horaria_unidade['UNIDADE'],
            mode="markers",
            name="Mínimo",
            marker=dict(color="red", size=10)
        ),
        go.Scatter(
            x=carga_horaria_unidade['Carga_Horaria_Maxima'],
            y=carga_horaria_unidade['UNIDADE'],
            mode="markers",
            name="Máximo",
            marker=dict(color="blue", size=10)
        ),
    ]

    # Adicionar a métrica selecionada (Média ou Mediana)
    if value == 'Média':
        fig_data.append(
            go.Scatter(
                x=carga_horaria_unidade['Carga_Horaria_Media'],
                y=carga_horaria_unidade['UNIDADE'],
                mode="markers",
                name="Média",
                marker=dict(color="green", size=10)
            )
        )
    elif value == 'Mediana':
        fig_data.append(
            go.Scatter(
                x=carga_horaria_unidade['Carga_Horaria_Mediana'],
                y=carga_horaria_unidade['UNIDADE'],
                mode="markers",
                name="Mediana",
                marker=dict(color="green", size=10)
            )
        )

    # Criar o gráfico
    fig = go.Figure(data=fig_data)

    fig.update_layout(
        title=dict(text="Carga horária semanal mínima e máxima dos docentes da Graduação"),
        height=1000,
        legend_itemclick=False,
    )

    return fig

@callback(
    Output('beeswarm-graph', 'figure'),
    Input('radio__selection-beeswarm', 'value')
)
def update_graph(value):
    df['color'] = 'Cinza'

    if value == 'Docente participa de laboratórios de pesquisa':
        # Linhas onde "Participação em laboratórios de pesquisa" > 0 recebem a cor azul
        df.loc[df['Participação em laboratórios de pesquisa'] > 0, 'color'] = 'Azul'
    else:
        # Linhas onde qualquer uma das colunas específicas > 0 recebem a cor azul
        df.loc[
            (df['Orientacao_Andamento_Mestrado'] > 0) |
            (df['Orientacao_Andamento_Doutorado'] > 0) |
            (df['Orientacao_Concluida_Mestrado'] > 0) |
            (df['Orientacao_Concluida_Doutorado'] > 0),
            'color'
        ] = 'Azul'

    categorias_ordenadas = sorted(df['UNIDADE'].unique())


    # Criação do gráfico
    figure = px.strip(
        df,
        x='UNIDADE',
        y='Orientacao_Concluida_TCC',
        color='color',
        color_discrete_map={'Cinza': 'gray', 'Azul': 'blue'},
        orientation='v',
        stripmode='overlay',
        hover_data=["DOCENTE"],
        category_orders={'UNIDADE': categorias_ordenadas},  # Ordem fixa no eixo X
    )

    # Customizações de layout
    figure.update_layout(
        xaxis_title='Unidade',
        yaxis_title='Orientações concluídas de TCC',
        plot_bgcolor='#fff',
        title=dict(
            text=f'Orientações concluídas de TCC por Unidade',
        ),
    )

    # Adiciona as linhas das grades
    figure.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='#e6e9f8',
        fixedrange=True,
    )

    figure.update_xaxes(fixedrange=True)

    return figure

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

        fig = px.bar(resultado_final, y="UNIDADE", x=["Soma total de publicações qualis A", "Soma total de publicações qualis B e sem qualis"], title="Soma de publicações por unidade", orientation="h")
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

        fig = px.bar(resultado_final, y="UNIDADE", x=["Soma total de publicações qualis A", "Soma total de publicações qualis B e sem qualis"], title="Soma de publicações por unidade", orientation="h")
        return fig

if __name__ == '__main__':
    app.run(debug=True)
