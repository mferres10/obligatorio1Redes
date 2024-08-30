from jsonrpc_redes.client import connect

if __name__ == "__main__":
    print('=============================')
    print('Iniciando pruebas de casos sin errores.')
    
    connS2 = connect('localhost', 8080)
    
    result = connS2.echo(message='No response!', notify=True)
    assert result == None
    print('Test de notificación completado.')
    connS2.close()
