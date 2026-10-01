import mysql.connector
import time

config = {
    'host' : 'localhost',
    'port' : 3306,
    'user' : 'nicolas',
    'password' : '12345',
        'database' : 'spot'
}


cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

while True:

    print("\n========== MENU ==========")
    print("1 - Visualizar CPU")
    print("2 - Visualizar RAM")
    print("3 - Visualizar Disco")
    print("4 - Sair")
    print("==========================")

    opcao = int(input("Escolha uma opção: "))
    print("Você digitou:", opcao)

    if opcao == 4:
        break

    if opcao == 1:
        nome = "CPU"

    elif opcao == 2:
        nome = "RAM"

    elif opcao == 3:
        nome = "DISCO"

    else:
        print("Opção inválida!")
        continue

    comando = """
        SELECT componente.nome, medida.tipo, leitura.valor, leitura.dia_hora
        FROM leitura
        JOIN componente
        ON leitura.fk_componente = componente.id_componente
        JOIN medida
        ON leitura.fk_medida = medida.id_medida
        WHERE componente.nome = %s
        ORDER BY leitura.dia_hora DESC
        LIMIT 5
    """

    cursor.execute(comando, (nome,)) #pra por nome no lugar %s, coloquei "(nome)"

    resultados = cursor.fetchall()

    print(f"\n========== {nome} ==========")

    for i in range(len(resultados)): #a função len() conta quantos resultados o banco trouxe, pq se o banco retornar menos que 5 registros, dará erro na consulta
     leitura = resultados[i]

    print(
        f"Componente: {leitura[0]} | "
        f"Medida: {leitura[1]} | "
        f"Valor: {leitura[2]} | "
        f"Data: {leitura[3]}"
    )

    time.sleep(3)

cursor.close()
cnx.close()
