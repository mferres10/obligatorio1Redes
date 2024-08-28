import socket
import json
import uuid

class Client:
    def __init__(self, address, port):
        self.address = (address, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)

    def __getattr__(self, name):
        def method(*args, **kwargs):
            notify = kwargs.get("notify", False)
            request = {
                "jsonrpc": "2.0",
                "method": name,
                "params": args,
                "id": str(uuid.uuid4()) if not notify else None
            }
            self.socket.sendall(json.dumps(request).encode('utf-8'))

            if not notify:
                response = self.socket.recv(1024).decode('utf-8')
                response_data = json.loads(response)
                if "error" in response_data:
                    raise Exception(f"RPC Error: {response_data['error']['message']}")
                return response_data.get("result")

        return method

    def close(self):
        self.socket.close()

def connect(address, port):
    return Client(address, port)
