# from starlette.applications import Starlette
# from starlette.responses import JSONResponse, HTMLResponse
# from starlette.routing import Route


# async def homepage(request):
#     return JSONResponse({'hello': 'world'})


# app = Starlette(debug=True, routes=[
#     Route('/', homepage),
# ])


from dash import Dash, Input, Output, callback, dcc, html

app = Dash(__name__, url_base_pathname="/_app/")

app.layout = html.Div(
    children=[
        dcc.Dropdown(id="dropdown", options=["red", "green", "blue", "orange"]),
        dcc.Markdown(id="markdown", children=["## Hello World"]),
    ]
)


@callback(
    Output("markdown", "style"),
    Input("dropdown", "value"),
)
def update_markdown_style(color):
    return {"color": color}


# import dash
# import dash_jc.components as dbc
# from dash import Input, Output, dcc, html

# app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], url_base_pathname="/_app/")


# # the style arguments for the sidebar. We use position:fixed and a fixed width
# SIDEBAR_STYLE = {
#     "position": "fixed",
#     "top": 0,
#     "left": 0,
#     "bottom": 0,
#     "width": "16rem",
#     "padding": "2rem 1rem",
#     "background-color": "#f8f9fa",
# }

# # the styles for the main content position it to the right of the sidebar and
# # add some padding.
# CONTENT_STYLE = {
#     "margin-left": "18rem",
#     "margin-right": "2rem",
#     "padding": "2rem 1rem",
# }

# sidebar = html.Div(
#     [
#         html.H2("Sidebar", className="display-4"),
#         html.Hr(),
#         html.P(
#             "A simple sidebar layout with navigation links", className="lead"
#         ),
#         dbc.Nav(
#             [
#                 dbc.NavLink("Home", href="/_app/", active="exact"),
#                 dbc.NavLink("Page 1", href="/_app/page-1", active="exact"),
#                 dbc.NavLink("Page 2", href="/_app/page-2", active="exact"),
#             ],
#             vertical=True,
#             pills=True,
#         ),
#     ],
#     style=SIDEBAR_STYLE,
# )

# content = html.Div(id="page-content", style=CONTENT_STYLE)

# app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
# def render_page_content(pathname):
#     if pathname == "/_app/":
#         return html.P("This is the content of the home page!")
#     elif pathname == "/_app/page-1":
#         return html.P("This is the content of page 1. Yay!")
#     elif pathname == "/_app/page-2":
#         return html.P("Oh cool, this is page 2!")
#     # If the user tries to reach a different page, return a 404 message
#     return html.Div(
#         [
#             html.H1("404: Not found", className="text-danger"),
#             html.Hr(),
#             html.P(f"The pathname {pathname} was not recognised..."),
#         ],
#         className="p-3 bg-light rounded-3",
#     )
