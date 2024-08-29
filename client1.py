from jsonrpc_redes.client import connect

if __name__ == "__main__":
    print('=============================')
    print('Iniciando pruebas de casos sin errores.')
    
    connS1 = connect('localhost', 8080)

    result = connS1.echo_concat(msg1='a', msg2='b', msg3='c', msg4='d')
    assert result == 'abcd'
    print('Test de múltiples parámetros con nombres completado')
