from jsonrpc_redes import connect

conn = connect('localhost', 5000)
print(conn.sum(3, 4))  # Debería imprimir 7
