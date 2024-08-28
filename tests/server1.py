from jsonrpc_redes import Server

def sum(a, b):
    return a + b

server = Server(('localhost', 5000))
server.add_method(sum)
server.serve()
