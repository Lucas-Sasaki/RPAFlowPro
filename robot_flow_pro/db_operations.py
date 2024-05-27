import mysql.connector

def chamar_procedure(dados):
    try:
        # Conectar ao banco de dados
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='14h1MP9982dr4.45',
            database='my_db'
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            print("Conectado ao servidor MySQL versão ", db_info)

            
            parametros = [tuple(x) for x in dados.to_numpy()]
            
            # Chamar a procedure
            cursor = connection.cursor()
            for tuplas in parametros:
                cursor.callproc('inserir_dados_tabela_flowpro', tuplas)
            
            connection.commit()
            print("Procedure chamada com sucesso!")

    except mysql.connector.Error as e:
        print("Erro ao conectar ou chamar a procedure:", e)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexão ao MySQL encerrada")
