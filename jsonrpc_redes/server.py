# jsonrpc_redes/server.py
import socket
import threading
import json

class Server:
    def __init__(self, address):
        self.address = address
        self.methods = {}

    def add_method(self, method):
        self.methods[method.__name__] = method

    def serve(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(self.address)
            server_socket.listen()
            print(f"Server listening on {self.address}")
            
            while True:
                client_socket, client_address = server_socket.accept()
                print(f"Connection from {client_address}")
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        with client_socket:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if data:
                    response = self.process_request(data)
                    client_socket.sendall(response.encode('utf-8'))
            except Exception as e:
                print(f"Error handling client: {e}")

    def process_request(self, request_data):
        try:
            request = json.loads(request_data)
            method_name = request.get("method")
            params = request.get("params", [])
            method = self.methods.get(method_name)

            if not method:
                return json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request.get("id")
                })

            result = method(*params)
            return json.dumps({
                "jsonrpc": "2.0",
                "result": result,
                "id": request.get("id")
            })

        except json.JSONDecodeError:
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"},
                "id": None
            })
        except Exception as e:
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": "Internal error"},
                "id": request.get("id")
            })
