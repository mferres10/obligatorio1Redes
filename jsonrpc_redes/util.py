import json

class Util:
    @staticmethod
    def readmsg(socket, max_iterations=20, buffer_size=4096, timeout=5):
        response_data = ""
        iteration = 0

        socket.settimeout(timeout)  # Establece el timeout para el socket

        while True:
            try:
                chunk = socket.recv(buffer_size).decode('utf-8')
                if not chunk:  # Detecta si la conexión se cerró y no hay más datos
                    raise RPCError(-32000 , "Connection closed by client")
                response_data += chunk
                iteration += 1
                # Intentar parsear para ver si ya recibimos el mensaje completo
                try:
                    json.loads(response_data)
                    return response_data  # Si json.loads no lanza una excepción, el JSON está completo
                except json.JSONDecodeError:
                    if iteration >= max_iterations:
                        print("Max iterations reached, closing connection")
                        raise json.JSONDecodeError
                    continue
            except TimeoutError:
                raise RPCError(-32000, "Connection timed out.")
            
class RPCError(Exception):
    def __init__(self, code, msg):
        super().__init__(f"RPCError {code}: {msg}")
        self.code = code
        self.message = msg
