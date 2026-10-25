import datetime as dt
import platform
import time
import uuid
import mysql.connector
import psutil as p

config = {
    "host": "localhost",
    "port": 3306,
    "user": "",
    "password": "",
    "database": "spot_bd",
}

conexao = mysql.connector.connect(**config)
cursor = conexao.cursor()

sistema = platform.system()

if sistema != "Linux":
    import machineid  
    uuid_atual = machineid.id()
else:
    uuid_atual = uuid.getnode()


def obter_id_maquina(uuid_maquina):
    sql = "SELECT id_servidor FROM servidor WHERE uuid = %s"
    cursor.execute(sql, (uuid_maquina,))
    resultado = cursor.fetchone()

    print(f"Resultado da busca por UUID: {resultado}")
    if resultado:
        return resultado[0]
    else:
        raise ValueError(
            f"Máquina com uuid '{uuid_maquina}' não foi encontrada na tabela Servidor."
        )


fk_maquina = obter_id_maquina(uuid_atual)


def verificacao_limites(fkMaquina):
    sql = "SELECT fk_servidor FROM configuracao WHERE fk_servidor = %s"
    cursor.execute(sql, (fkMaquina,))
    resultado = cursor.fetchall()  

    return resultado is not None


def limites_default(fkMaquina, fkMetrica, limite):
    sql = "INSERT INTO configuracao (fk_servidor, fk_componente, limite) VALUES (%s, %s, %s)"
    cursor.execute(sql, (fkMaquina, fkMetrica, limite))
    conexao.commit()  


dados_metricas = [(1, 70.0), (2, 80.0), (3, 85.0), (4, 50.0)]

if not verificacao_limites(fk_maquina):
    print(
        f"Configurando os limites padrões para a máquina {fk_maquina}..."
    )
    for fk_metrica, limite in dados_metricas:
        limites_default(fk_maquina, fk_metrica, limite)
    print("Configuração padrão inserida com sucesso!")
else:
    print("Os limites para esta máquina já estão configurados no banco.")


def insert_leitura(fkMaquina):
    print("Iniciando monitoramento de hardware... ")     

    try: 
        while True:
            agora = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            uso_cpu = p.cpu_percent(interval=1)
            uso_memoria = p.virtual_memory().percent

            if sistema != "Linux":
                uso_disco = p.disk_usage('C:\\').percent 
            else: 
                uso_disco = p.disk_usage('/').percent+80

            leituras = [
                (uso_cpu, 1, "CPU"),
                (uso_memoria, 3, "Memória RAM"),
                (uso_disco, 2, "Disco")
            ]

            dados_para_verificacao = []

            for valor, fk_componente, nome in leituras:
                sql = """
                    INSERT INTO leitura (valor, dia_hora, fk_configComponente, fk_configServidor) 
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (valor, agora, fk_componente, fkMaquina))
                conexao.commit()

                dados_para_verificacao.append({
                    "fk_componente": fk_componente,
                    "nome": nome,
                    "valor": valor,
                    "id_leitura": cursor.lastrowid
                })

            print(f"[{agora}] Leitura inserida -> CPU:{uso_cpu}% | RAM:{uso_memoria}% | DISCO:{uso_disco}%")

            for item in dados_para_verificacao:
                fk_componente = item["fk_componente"]
                nome = item["nome"]
                valor = item["valor"]
                id_leitura_atual = item["id_leitura"]

                sql_limite = "SELECT limite FROM configuracao WHERE fk_servidor = %s AND fk_componente = %s"
                cursor.execute(sql_limite, (fkMaquina, fk_componente))
                res_limite = cursor.fetchone()

                if not res_limite:
                    raise ValueError(f"Erro crítico: O componente {fk_componente} não possui limite configurado!")

                limite_configurado = res_limite[0]
                margem_atencao = limite_configurado - 5.0

                if valor >= limite_configurado:
                    grau = "Crítico"
                    sql_alerta = "INSERT INTO alerta (grau_alerta, fk_leitura) VALUES (%s, %s)"
                    cursor.execute(sql_alerta, (grau, id_leitura_atual))
                    conexao.commit()
                    print(f"ALERTA CRÍTICO! {nome} atingiu {valor}% (Limite: {limite_configurado}%)")
             
                elif valor >= margem_atencao:
                    print(f"ATENÇÃO! {nome} está em {valor}% (Próximo do limite de {limite_configurado}%)")
            
                else:
                    print(f"{nome}: {valor}% (Normal)")

            time.sleep(5)

    except KeyboardInterrupt:
        print('\nLeitura encerrada pelo usuário')

insert_leitura(fk_maquina)
cursor.close()
conexao.close()
