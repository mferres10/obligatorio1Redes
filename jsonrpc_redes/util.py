import json

class Util:
    @staticmethod
    def readmsg(socket, max_iterations=40, buffer_size=4096, timeout=10):
        response_data = ""
        iteration = 0

        socket.settimeout(timeout)  # Establece el timeout para el socket

        while True:
            try:
                chunk = socket.recv(buffer_size).decode('utf-8')
                if not chunk:  # Detecta si la conexión se cerró y no hay más datos
                    raise RPCError(-32001 , "Connection closed by client")
                response_data += chunk
                # Intentar parsear para ver si ya recibimos el mensaje completo
                try:
                    json.loads(response_data)
                    print(response_data)
                    return response_data  # Si json.loads no lanza una excepción, el JSON está completo
                except json.JSONDecodeError:
                    if iteration >= max_iterations:
                        print("Max iterations reached, closing connection")
                        raise RPCError(0, "Connection reached max Iterations.")
                    #SI EL JSON ESTA INCOMPLETO SIGO LEYENDO
                    if Util.is_wellformed_json(response_data):
                        iteration += 1
                    else:
                        raise RPCError(-32700, "Invalid JSON.")
            except TimeoutError:
                raise TimeoutError
            
    @staticmethod
    def is_wellformed_json(data):
        stack = []
        in_string = False
        escape = False

        for char in data:
            if char == '"' and not escape:
                in_string = not in_string
            elif not in_string:
                if char == '{' or char == '[':
                    stack.append(char)
                elif char == '}' :
                    if (stack and stack[-1] == '{'):
                        stack.pop()
                    else :
                        return False
                elif char == ']':
                    if (stack and stack[-1] == '['):
                        stack.pop()
                    else :
                        return False
            # Handle escape sequences (e.g., \")
            if char == '\\' and not escape:
                escape = True
            else:
                escape = False

        # si el stack no esta vacio o esta detro de un string y json va bien formado pero aun no esta completo
        return len(stack) > 0 or in_string

class RPCError(Exception):
    def __init__(self, code, msg):
        super().__init__(f"RPCError {code}: {msg}")
        self.code = code
        self.message = msg
