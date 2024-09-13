from jsonrpc_redes import Server
import threading
import time
import sys
SERVERIP = '200.100.0.15'

def test_server1():
    host, port = SERVERIP, 8080

    def sumar(a, b):
        return a + b

    def restar(a, b):
        return a - b

    def concatenar(s1, s2):
        return s1 + s2
    
    def echo(message):
        return message
        
    def summation(*args):
        return sum(args)

    def echo_concat(msg1, msg2, msg3, msg4):
        return msg1 + msg2 + msg3 + msg4

    server = Server((host, port))
    server.add_method(sumar)
    server.add_method(restar)
    server.add_method(concatenar)
    server.add_method(echo)
    server.add_method(summation, 'sum')
    server.add_method(echo_concat)
    server_thread = threading.Thread(target=server.serve)
    server_thread.daemon = True
    server_thread.start()

    print(f"Servidor 1 corriendo en {host}:{port}")
    
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        server.shutdown()
        print('Terminado server valido.')

def test_server_invalid_method_name():
    host, port = SERVERIP, 8080

    def rpctest(message):
        return message
    
    server = Server((host, port))

    try :
        server.add_method(rpctest, 'rpc.test')
    except Exception as e:
        print("Server tira exception al intentar agregar un nombre de metodo invalido.")


if __name__ == "__main__":
    test_server1()
    test_server_invalid_method_name()