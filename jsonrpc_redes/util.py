import json

class Util:
    @staticmethod
    def readmsg(socket, max_iterations=20, buffer_size=1024, timeout=5):
        response_data = ""
        iteration = 0

        socket.settimeout(timeout)  # Establece el timeout para el socket

        while True:
            try:
                chunk = socket.recv(buffer_size).decode('utf-8')
                if not chunk:  # Detecta si la conexión se cerró y no hay más datos
                    print("Connection closed by client")
                    break
                    return None
                response_data += chunk
                iteration += 1
                # Intentar parsear para ver si ya recibimos el mensaje completo
                try:
                    json.loads(response_data)
                    return response_data  # Si json.loads no lanza una excepción, el JSON está completo
                except json.JSONDecodeError:
                    if iteration >= max_iterations:
                        print("Max iterations reached, closing connection")
                        break
                    continue
            except socket.timeout:
                    raise Exception("Connection timed out.")
        raise json.JSONDecodeError  # Si se alcanza el máximo de iteraciones, salir del bucle

