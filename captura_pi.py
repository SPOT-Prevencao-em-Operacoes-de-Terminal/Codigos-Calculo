import psutil as p
from mysql.connector import connect, Error
import time
import datetime as dt
import random

config = {
    'host' : 'localhost',
    'port' : 3306,
    'user' : 'nicolas',
    'password' : '12345',
    'database' : 'spot'
}

cnx = connect(**config)    
cursor = cnx.cursor()

while True:
    temp_cpu = random.randint(40, 80) 

    #conexoes importantes
    estabelecido_api = 0
    estabelecido_sql = 0
    conexoes = p.net_connections()
    for conexao in conexoes:
        if conexao.laddr and conexao.laddr.port == 8080 and conexao.status == 'LISTEN':
            estabelecido_api = 1
        if conexao.laddr and conexao.laddr.port == 3306 and conexao.status == 'LISTEN':
            estabelecido_sql = 1

    #valores simples
    porcent_cpu =  p.cpu_percent(interval = 1)
    porcent_ram =  p.virtual_memory().percent
    porcent_swap = p.swap_memory().percent
    porcent_disk = p.disk_usage("/").percent

    
    #tuplas a inserir
    dia_hora = dt.datetime.now()
    valores = [
    (1, 1, porcent_cpu, dia_hora),
    (2, 1, porcent_ram, dia_hora),
    (2, 6, porcent_swap, dia_hora),
    (3, 1, porcent_disk, dia_hora),
    (1, 4, temp_cpu, dia_hora),
    (4, 8, estabelecido_api, dia_hora),
    (4, 9, estabelecido_sql, dia_hora)
]

# blocos de discretização inicio

    if porcent_cpu > 85:
     situacao = 3
    elif porcent_cpu >= 75:
     situacao = 2
    else:  
      situacao = 1

    valores[0] += (situacao,)


    if porcent_ram >= 95:
     situacao = 3
    elif porcent_ram >= 85:
      situacao = 2
    else:
     situacao = 1

    valores[1] += (situacao,)


    if porcent_swap >= 70:
     situacao = 3
    else:
     situacao = 1

    valores[2] += (situacao,)


    if porcent_disk >= 95:
     situacao = 3
    elif porcent_disk >= 90:
     situacao = 2
    else:
     situacao = 1

    valores[3] += (situacao,)


    if temp_cpu >= 95:
     situacao = 3
    elif temp_cpu >= 90:
     situacao = 2
    else:
     situacao = 1

    valores[4] += (situacao,)


    if estabelecido_api == 1:
      situacao = 1
    else:
     situacao = 3

    valores[5] += (situacao,)


    if estabelecido_sql == 1:
     situacao = 1
    else:
      situacao = 3

    valores[6] += (situacao,)

# blocos de discretização fim
    print(valores)


    comando = "INSERT INTO leitura (fk_componente, fk_medida, valor, dia_hora, alerta) VALUES (%s, %s, %s, %s, %s)"
    cursor.executemany(comando, valores)
    cnx.commit()

    time.sleep(5)


    

    
    
