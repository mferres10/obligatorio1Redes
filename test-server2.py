from jsonrpc_redes import Server
import threading
import time
import sys
SERVERIP = 'localhost'

def test_server2():
    host, port = SERVERIP, 8081

    def multiplicar(a, b):
        return a * b

    def dividir(a, b):
        if b == 0:
            raise ValueError("No se puede dividir por cero")
        return a / b

    def concatenar_con_separador(s1, s2, separador):
        return f"{s1}{separador}{s2}"

    server = Server((host, port))
    server.add_method(multiplicar)
    server.add_method(dividir)
    server.add_method(concatenar_con_separador)
    server_thread = threading.Thread(target=server.serve)
    server_thread.daemon = True
    server_thread.start()

    print(f"Servidor 2 corriendo en {host}:{port}")
    
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        server.shutdown()
        print('Terminado.')
        sys.exit()

if __name__ == "__main__":
    test_server2()
