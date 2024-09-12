# jsonrpc_redes/server.py
import socket
import threading
import json
from .util import Util
from .util import RPCError

class Server:
    def __init__(self, address):
        self.address = address
        self.methods = {}
        self.threads = []  # List to keep track of active threads
        self.running = True  # A flag to control the server loop

    def add_method(self, method, name=None):
        if name is None:
            name = method.__name__
        # Validar que el nombre del método no comience con "rpc."
        if name.startswith('rpc.'):
            raise ValueError(f"El nombre del método '{name}' está reservado y no puede comenzar con 'rpc.'")
        self.methods[name] = method

    def serve(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.address)
        self.server_socket.listen()
        print(f"Server listening on {self.address}")
        
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(f"Connection from {client_address}")
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
                self.threads.append(client_thread)
            except OSError:
                break  # Break the loop if the socket is closed
        for thread in self.threads:
            thread.join()
        self.server_socket.close()

    def handle_client(self, client_socket):
        parsed_data = None      
        while True:
            try:
                # Lee una sola request del cliente utilizando la lógica de readmsg en la clase Util
                unparsed_data = Util.readmsg(client_socket)
                if unparsed_data:
                    parsed_data = json.loads(unparsed_data)
                    response = self.process_request(parsed_data)
                    parsed_data = None
                    if response is not None:
                        client_socket.sendall(response.encode('utf-8'))
                    else:
                        continue

            except RPCError as e:
                # Handle RPCError by checking the error code
                if e.code == -32700:
                    # Send a "Parse error" response back to the client
                    response = json.dumps({
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": "Parse error"},
                        "id": None
                    })
                    client_socket.sendall(response.encode('utf-8'))
                    continue
                # Si se superaron las iteraciones y el JSON seguia sin poder parsearse seguramente sea un cliente malicioso
                elif e.code == 0:
                    # Close the connection immediately for error codes 0 or 1
                    print(f"Client connection closed due to error code {e.code}: {e.message}")
                    break  # Exit the loop and close the connection
                else:
                    print(f"Client error: {e.message}")
                    break  # For other error codes, exit the loop and close the connection
                
            except TimeoutError:
                print("Connection timed out")
                break  # Salir del bucle si se alcanza el timeout

            except Exception as e:
                break  # Salir del bucle en caso de otras excepciones
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
                        "error": {"code": -32600, "message": "Invalid Request"},
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
                    if isinstance(params, dict):
                        # Si los parámetros son un diccionario, se pasan como **kwargs
                        result = method(**params)
                    else:
                        # Si los parámetros son una lista, se pasan como *args
                        result = method(*params)
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
            
    def shutdown(self):
        self.running = False
        self.server_socket.close()



