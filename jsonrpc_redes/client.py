import socket
import json
import uuid
from .util import Util

class Client:
    def __init__(self, address, port):
        self.address = (address, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)

    def __getattr__(self, name):
        def method(*args, **kwargs):
            notify = kwargs.pop("notify", False)
            
            # Verificar si hay una mezcla de argumentos posicionales y nombrados
            if args and kwargs:
                raise Exception("No se pueden mezclar argumentos posicionales y nombrados en una llamada RPC según la especificación JSON-RPC 2.0.")

            # Si solo hay argumentos posicionales, los usamos como lista
            if args:
                params = list(args) 
            # Si solo hay argumentos nombrados, los usamos como diccionario
            elif kwargs:
                params = kwargs
            else:
                params = []

            request = {
                "jsonrpc": "2.0",
                "method": name,
                "params": params,
                "id": str(uuid.uuid4()) if not notify else None
            }
            jsonRequest = json.dumps(request)
            print(request)
            self.socket.sendall(jsonRequest.encode('utf-8'))

            if not notify :
                try:
                    # Uso el método Util.readmsg para recibir la respuesta
                    unparsed_data = Util.readmsg(self.socket)
                    print(unparsed_data)
                    if not unparsed_data:
                        print("No se.")

                    parsed_data = json.loads(unparsed_data)
                    if "error" in parsed_data:
                        # El SV retorno un mensaje de error asi que throweo esa exception
                        raise Exception(f"RPC Error: {parsed_data['error']['message']}")
                    else :
                        return parsed_data.get("result")
                    
                except socket.timeout:
                    raise Exception("Connection timed out.")
                except Exception as e:
                    raise e
            else :
                return None
        return method

    def close(self):
        self.socket.close()

def connect(address, port):
    return Client(address, port)
