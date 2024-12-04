import dash
from dash import html, dcc, callback, Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

dash.register_page(__name__)

df = pd.read_csv('user_answers2022-2023teste.csv')

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
    title=dict(
            text='Orientações concluídas e em andamento por Docente - Pós-graduação',
            y=0.85,
            xanchor='left',
            font=dict(
                size=20,
                color='black',
                weight='bold'
            ),
        ),
    xaxis_title='Orientações em andamento por docente',
    yaxis_title='Unidade',
    # font=dict(
    #     size=14,  # Set the font size here
    # )
)

media_pos_bargraph.update_traces(textposition='inside', textfont_size=18)

layout = html.Main([
            html.H2(id='', className='mainpage__subtitle', children='Orientações de trabalhos'),
            html.P(children='Cor dos professores: ', className='body__text'),
            dcc.RadioItems(['Docente de pós graduação', 'Docente participa de laboratórios de pesquisa'], 'Docente de pós graduação', inline=True, id='radio__selection-beeswarm', className='body__text'),
            dcc.Graph(id='beeswarm-graph'),
            dcc.Graph(figure=media_pos_bargraph),
])

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
            text='Orientações concluídas de TCC por Unidade',
            y=0.93,
            xanchor='left',
            font=dict(
                size=20,
                color='black',
                weight='bold'
            ),
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