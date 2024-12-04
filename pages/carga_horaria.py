import dash
from dash import html, dcc, callback, Input, Output
import pandas as pd
import plotly.graph_objects as go

dash.register_page(__name__, path='/')

df = pd.read_csv('user_answers2022-2023teste.csv')
units = sorted(df['UNIDADE'].unique())

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
violin.update_layout(
    title=dict(
            text='Carga horária semanal na graduação, pós-graduação e cursos lato sensu, presencial ou EAD, por unidade',
            y=0.85,
            xanchor='left',
            font=dict(
                size=20,
                color='black',
                weight='bold'
            ),
        ),
    )

layout = html.Main([
            html.H2(id='', className='mainpage__subtitle', children='Carga horária docente'),
            html.P(children='Métrica utilizada: ', className='body__text'),
            dcc.RadioItems(['Média', 'Mediana'], 'Média', inline=True, id='radio__selection-lollipop', className='body__text'),
            dcc.Graph(id='lollipop-graph'),
            dcc.Graph(figure=violin),
])

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
        title=dict(
            text='Carga horária semanal, mínima e máxima, dos docentes da Graduação',
            y=0.93,
            xanchor='left',
            font=dict(
                size=20,
                color='black',
                weight='bold'
            ),
        ),
        height=1000,
        legend_itemclick=False,
    )

    return fig