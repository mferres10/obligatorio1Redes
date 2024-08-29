# jsonrpc_redes/server.py
import socket
import threading
import json
from .util import Util

class Server:
    def __init__(self, address):
        self.address = address
        self.methods = {}

    def add_method(self, method, name=None):
        if name is None:
            name = method.__name__
        self.methods[name] = method

    def serve(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.address)
        self.server_socket.listen()
        print(f"Server listening on {self.address}")
        
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Connection from {client_address}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()      
        self.server_socket.close()

    def handle_client(self, client_socket):
        try:
            parsed_data = None
            while True:
                try:
                    # Lee una sola request del cliente utilizando la lógica de readmsg en la clase Util
                    unparsed_data = Util.readmsg(client_socket)
                    if unparsed_data:
                        parsed_data = json.loads(unparsed_data)
                        response = self.process_request(parsed_data)
                        parsed_data = None
                        print(response)
                        if response is not None:
                            client_socket.sendall(response.encode('utf-8'))
                        else:
                            continue

                # Si se superaron las 20 iteraciones y el JSON seguia sin poder parsearse seguramente el JSON sea invalido
                except json.JSONDecodeError:
                    response = json.dumps({
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": "Parse error"},
                        "id": None
                    })
                    client_socket.sendall(response.encode('utf-8'))
                    continue  # Continúa esperando nuevas solicitudes

                except socket.timeout:
                    print("Connection timed out")
                    break  # Salir del bucle si se alcanza el timeout

                except Exception as e:
                    print(f"Error reading message: {e}")
                    break  # Salir del bucle en caso de otras excepciones


        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()


    def process_request(self, request_data):
        if not "id" in request_data:
            return None
        else:
            try:
                id = request_data.get("id", None)
                # Validación de la estructura básica de la solicitud JSON-RPC
                if "jsonrpc" not in request_data or request_data["jsonrpc"] != "2.0" or \
                "method" not in request_data or not isinstance(request_data["method"], str):
                    return json.dumps({
                        "jsonrpc": "2.0",
                        "error": {"code": -32600, "message": "Invalid request_data"},
                        "id": id  # El campo "id" puede no estar presente
                    })

                method_name = request_data.get("method")
                params = request_data.get("params", [])
                method = self.methods.get(method_name)

                if not method:
                    return json.dumps({
                        "jsonrpc": "2.0",
                        "error": {"code": -32601, "message": "Method not found"},
                        "id": id 
                    })

                try:
                    result = method(*params)
                    print(result)
                except TypeError:
                    return json.dumps({
                        "jsonrpc": "2.0",
                        "error": {"code": -32602, "message": "Invalid params"},
                        "id": id 
                    })

                return json.dumps({
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": id
                })

            except Exception:
                return json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": "Internal error"},
                    "id": id
                })


