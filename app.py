from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash
import flask

app = Dash(__name__, use_pages=True)

# Layout com um componente dcc.Location para capturar o pathname da URL
app.layout = html.Div([
    html.H1('Relatório de Atividades Docentes (RAD) 2023 - Tópicos Avançados em Sistemas de Informação II', className='mainpage__title'),
    html.Nav([
            html.Div(
                dcc.Link(f"{page['name']}", href=page["relative_path"], className='link-a'), className='link-div'
            ) for page in dash.page_registry.values()
    ], className='main__navbar'),
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=True)
