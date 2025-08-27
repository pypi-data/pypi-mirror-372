dash = """
dash
pyodide_http
ssl
"""

vizro = dash

tornado = """
tornado
ssl
pyzmq==24.0 # mock
psutil==5.9.8 # mock
argon2-cffi-bindings==21.2.0 # mock
pyodide_http
"""

panel = tornado

streamlit = (
    tornado
    + """
streamlit
watchdog # mock
sqlite3
setuptools
"""
)

shiny = """
ssl
sqlite3
setuptools
shiny
"""

solara = (
    tornado
    + """
setuptools
debugpy==1.8.1 # mock
pexpect==4.9.0 # mock
notebook==6.5 # mock
nbclassic==1.1.0 # mock
watchdog==4.0.0 # mock
watchfiles==0.21.0 # mock
jupyter-server==2.10.0 # mock
starlette==0.32.0
sqlite3
ipython==8.16.1
ipykernel==6.25.2
solara==1.33.0
pyodide_http
rpds-py==0.18.0 # mock
"""
)
