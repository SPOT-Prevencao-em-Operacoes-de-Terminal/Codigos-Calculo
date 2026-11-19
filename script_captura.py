import datetime as dt
import platform
import time
import uuid
import os
import smtplib
import mysql.connector
import psutil as p
from email.message import EmailMessage

config = {
    "host": "localhost",
    "port": 3306,
    "user": "user_SPOT",
    "password": "SPOT2026!",
    "database": "spot_bd",
}

conexao = mysql.connector.connect(**config)
cursor = conexao.cursor()

sistema = platform.system()

if sistema != "Linux":
    import machineid
    uuid_atual = machineid.id()
else:
    uuid_atual = str(uuid.getnode())


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


def obter_dados_servidor(fkMaquina):
    sql = "SELECT hostname, fk_empresa FROM servidor WHERE id_servidor = %s"
    cursor.execute(sql, (fkMaquina,))
    resultado = cursor.fetchone()

    if resultado:
        return resultado[0], resultado[1]
    else:
        raise ValueError(f"Servidor {fkMaquina} não encontrado.")


hostname_servidor, fk_empresa = obter_dados_servidor(fk_maquina)


def buscar_emails_empresa(fkEmpresa):
    sql = """
        SELECT DISTINCT c.contatocol
        FROM usuario u
        JOIN contato c ON c.fk_usuario = u.id_usuario
        JOIN tipo_contato tc ON tc.idtipo_contato = c.fk_tipo_contato
        WHERE u.fk_empresa = %s
        AND u.status = 'Ativo'
        AND tc.nome = 'E-mail'
    """
    cursor.execute(sql, (fkEmpresa,))
    resultado = cursor.fetchall()

    emails = [item[0] for item in resultado if item[0]]
    return emails


def enviar_email(destinatarios, assunto, mensagem):
    remetente = os.getenv("SPOT_EMAIL_REMETENTE")
    senha = os.getenv("SPOT_EMAIL_SENHA")
    if senha:
        senha = senha.replace(" ", "")

    if not remetente or not senha:
        print("AVISO: Configure SPOT_EMAIL_REMETENTE e SPOT_EMAIL_SENHA para enviar e-mails.")
        return False

    if not destinatarios:
        print("AVISO: Não existem usuários ativos com e-mail cadastrado nesta empresa.")
        return False

    email = EmailMessage()
    email["From"] = remetente
    email["To"] = "Usuários ativos da empresa"
    email["Bcc"] = ", ".join(destinatarios)
    email["Subject"] = assunto
    email.set_content(mensagem)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor_email:
            servidor_email.login(remetente, senha)
            servidor_email.send_message(email)

        print(f"E-mail enviado para {len(destinatarios)} usuário(s).")
        return True

    except Exception as erro:
        print(f"ERRO ao enviar e-mail: {erro}")
        return False


def notificar_mudanca_estado(nome, valor, limite, estado, estado_anterior, agora):
    destinatarios = buscar_emails_empresa(fk_empresa)

    if estado == "Atenção":
        assunto = f"SPOT | Atenção: utilização elevada de {nome}"
        situacao = "está próxima do limite configurado"
        recomendacao = "Recomendamos acompanhar o comportamento do servidor para evitar que o limite seja ultrapassado."

    elif estado == "Crítico":
        assunto = f"SPOT | ALERTA CRÍTICO: limite de {nome} atingido"
        situacao = "atingiu ou ultrapassou o limite configurado"
        recomendacao = "Recomendamos verificar imediatamente o servidor para identificar possíveis causas da sobrecarga."

    else:
        assunto = f"SPOT | Normalização: {nome}"
        situacao = "retornou a uma condição normal de utilização"
        recomendacao = "A métrica voltou a ficar abaixo da faixa de atenção. Continue acompanhando o servidor."

    mensagem = f"""Olá!

O sistema SPOT identificou uma mudança no estado de monitoramento do servidor {hostname_servidor}.

Componente: {nome}
Utilização atual: {valor}%
Limite configurado: {limite}%
Situação atual: {estado}
Situação anterior: {estado_anterior}
Data e horário: {agora}

A métrica {situacao}.

{recomendacao}

Esta é uma notificação automática do sistema SPOT.
"""

    enviar_email(destinatarios, assunto, mensagem)


def verificacao_limites(fkMaquina, fkMetrica):
    sql = "SELECT fk_servidor FROM configuracao WHERE fk_servidor = %s AND fk_componente = %s"
    cursor.execute(sql, (fkMaquina, fkMetrica))
    resultado = cursor.fetchone()

    return resultado is not None


def limites_default(fkMaquina, fkMetrica, limite):
    sql = "INSERT INTO configuracao (fk_servidor, fk_componente, limite) VALUES (%s, %s, %s)"
    cursor.execute(sql, (fkMaquina, fkMetrica, limite))
    conexao.commit()


dados_metricas = [(1, 70.0), (2, 80.0), (3, 85.0)]

for fk_metrica, limite in dados_metricas:
    if not verificacao_limites(fk_maquina, fk_metrica):
        print(f"Configurando limite padrão para o componente {fk_metrica}...")
        limites_default(fk_maquina, fk_metrica, limite)


# Guarda o último estado de cada componente durante a execução do script.
estados_componentes = {}


def insert_leitura(fkMaquina):
    print("Iniciando monitoramento de hardware...")

    try:
        while True:
            agora = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            uso_cpu = p.cpu_percent(interval=1)
            uso_memoria = p.virtual_memory().percent

            if sistema != "Linux":
                uso_disco = p.disk_usage('C:\\').percent
            else:
                uso_disco = p.disk_usage('/').percent

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
                    estado_atual = "Crítico"
                elif valor >= margem_atencao:
                    estado_atual = "Atenção"
                else:
                    estado_atual = "Normal"

                estado_anterior = estados_componentes.get(fk_componente, "Normal")

                if estado_atual != estado_anterior:
                    if estado_atual != "Normal":
                        sql_alerta = "INSERT INTO alerta (grau_alerta, fk_leitura) VALUES (%s, %s)"
                        cursor.execute(sql_alerta, (estado_atual, id_leitura_atual))
                        conexao.commit()

                    notificar_mudanca_estado(
                        nome,
                        valor,
                        limite_configurado,
                        estado_atual,
                        estado_anterior,
                        agora
                    )

                    estados_componentes[fk_componente] = estado_atual

                if estado_atual == "Crítico":
                    print(f"ALERTA CRÍTICO! {nome} atingiu {valor}% (Limite: {limite_configurado}%)")
                elif estado_atual == "Atenção":
                    print(f"ATENÇÃO! {nome} está em {valor}% (Próximo do limite de {limite_configurado}%)")
                else:
                    print(f"{nome}: {valor}% (Normal)")

            time.sleep(5)

    except KeyboardInterrupt:
        print('\nLeitura encerrada pelo usuário')


insert_leitura(fk_maquina)
cursor.close()
conexao.close()
