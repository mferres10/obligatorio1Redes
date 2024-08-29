from jsonrpc_redes.server import Server

def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

if __name__ == "__main__":
    server = Server(('localhost', 5000))
    server.add_method(add)
    server.add_method(subtract)
    server.serve()
