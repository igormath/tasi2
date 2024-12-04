from dash import Dash, html, dcc, callback, Output, Input
import dash

app = Dash(__name__, use_pages=True)

# Layout com um componente dcc.Location para capturar o pathname da URL
app.layout = html.Div([
    html.Header(id='', className='main__header', children=[
        html.H1('Relatório de Atividades Docentes (RAD) 2023', className='mainpage__title'),
        html.Nav([
                html.Div(
                    dcc.Link(f"{page['name']}", href=page["relative_path"], className='link-a'), className='link-div'
                ) for page in dash.page_registry.values()
        ], className='main__navbar'),
    ]),
    dash.page_container,
    html.Footer([
        html.H3(className='footer__subtitle', children='Integrantes: '),
        html.Ul([
            html.Li('Carlle Oliveira'),
            html.Li('Gabriela Isabel'),
            html.Li('Igor Matheus'),
            html.Li('Kaelany Soares'),
            html.Li('Raysa Leal'),
        ]),
        html.P('Tópicos Avançados em Sistemas de Informação II (2024.2) - Universidade de Pernambuco')
    ], className="main__footer")
])

if __name__ == '__main__':
    app.run(debug=True)
