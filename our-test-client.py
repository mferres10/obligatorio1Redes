from jsonrpc_redes import connect
import socket
import json
from jsonrpc_redes import Util
LOCALHOST = '200.100.0.15'
SERVER2 = '200.0.0.10'
LOCALHOST = 'localhost'


def test_valid_scenario():
    print("Escenario valido...")
    conn = connect(LOCALHOST, 8080)

    # Test successful method calls
    assert conn.echo('Hello') == 'Hello'
    assert conn.echo_concat('a', 'b', 'c', 'd') == 'abcd'
    assert conn.sum(1, 2, 3, 4, 5) == 15

    print("Escenario valido Bien!")
    conn.close()

def test_invalid_method():
    print("Metodo no existe...")

    conn = connect(LOCALHOST, 8080)

    try:
        conn.non_existent_method()
    except Exception as e:
        print(f"{e}")
    
    conn.close()

def test_invalid_params():
    print("Test parametros invalidos...")

    conn = connect(LOCALHOST, 8080)

    try:
        conn.echo_concat('a', 'b')  # Missing parameters
    except Exception as e:
        print(f"{e}")
    finally:
        conn.close()

def test_timeout():
    print("Test timeout...")

    # Create a raw socket connection and send incomplete/invalid JSON
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((LOCALHOST, 8080))

    invalid_json = '{"jsonrpc": "2.0", "method": "echo", "params": ["Hello"],'  # JSON incompleto deberia bloquearse el receive y tirar timeout
    client_socket.sendall(invalid_json.encode('utf-8'))
    print("Test timeout, servidor deberia cerrar la aplicacion...")

def test_timeout2():
    print("Test timeout...")

    # Create a raw socket connection and send incomplete/invalid JSON
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((LOCALHOST, 8080))

    invalid_json = '{"jsonrpc": "2.0", "method": "echo", "params": ["Hello"],'  # JSON incompleto deberia bloquearse el receive y tirar timeout
    client_socket.sendall(invalid_json.encode('utf-8'))
    print("Test timeout, servidor deberia cerrar la aplicacion...")


def test_JSONInvalido():
    print("Test JSON Invalido...")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((LOCALHOST, 8080))

    invalid_json = '{"jsonrpc": "2.0", "methoddinho": "echo", "parametrinhos": "He"]'  # JSON invalido deberia poder parsearlo pero fallar
    print(Util.is_wellformed_json(invalid_json))
    client_socket.sendall(invalid_json.encode('utf-8'))
    response = client_socket.recv(4096).decode('utf-8')
    response_data = json.loads(response)

    print("Respuesta:", response_data)
    assert response_data['error']['code'] == -32700
    assert response_data['error']['message'] == 'Parse error'

    client_socket.close()

def test_client_disconnect():
    print("Testing client disconnection...")

    # Connect and send a valid request but disconnect before getting a response
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((LOCALHOST, 8080))

    valid_request = json.dumps({
        "jsonrpc": "2.0",
        "method": "echo",
        "params": ["Hello"],
        "id": "1"
    })
    client_socket.sendall(valid_request.encode('utf-8'))

    # Close the connection immediately
    client_socket.close()

    print("Client disconnected before receiving the response.")

def test_cliente_cruzado():
    print("Conectando al Servidor 1...")
    conn1 = connect('localhost', 8080)

    print("Conectando al Servidor 2...")
    conn2 = connect('localhost', 8081)

    # Llamadas exitosas al Servidor 1
    print("Probando sumar en Servidor 1...")
    assert conn1.sumar(10, 5) == 15
    print("Probando restar en Servidor 1...")
    assert conn1.restar(10, 5) == 5
    print("Probando concatenar en Servidor 1...")
    assert conn1.concatenar("Hola", "Mundo") == "HolaMundo"

    # Llamadas exitosas al Servidor 2
    print("Probando multiplicar en Servidor 2...")
    assert conn2.multiplicar(3, 4) == 12
    print("Probando dividir en Servidor 2...")
    assert conn2.dividir(10, 2) == 5.0
    print("Probando concatenar con separador en Servidor 2...")
    assert conn2.concatenar_con_separador("Hola", "Mundo", " ") == "Hola Mundo"

    # Probando errores
    try:
        print("Probando método no existente en Servidor 1...")
        conn1.no_existe()
    except Exception as e:
        print(f"Error esperado: {e}")

    try:
        print("Probando división por cero en Servidor 2...")
        conn2.dividir(10, 0)
    except Exception as e:
        print(f"Error esperado: {e}")

    # Cerrando conexiones
    conn1.close()
    conn2.close()

if __name__ == "__main__":
    test_valid_scenario()
    test_invalid_method()
    test_invalid_params()
    test_JSONInvalido()
    test_timeout()
    test_timeout2()
    test_client_disconnect()
    test_cliente_cruzado()

