import socket

from textual_serve.server import Server

ip = socket.gethostbyname(socket.gethostname())
port = 8000
print(ip)
server = Server(r"python .\src\app.py", host=ip, port=port)
server.serve(debug=False)
