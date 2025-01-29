import os
import csv
import psycopg2
from datetime import datetime
import subprocess
import requests

# Função para criar diretórios se não existirem
def create_directory(path):
    os.makedirs(path, exist_ok=True)

# Função para salvar os dados em arquivos CSV
def save_to_local_disk(data, path, file_name):
    create_directory(path)
    file_path = os.path.join(path, file_name)
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    print(f"Data saved to {file_path}")

# Função para executar comandos SQL no novo banco de dados
def execute_sql_commands(conn, sql_commands):
    try:
        cursor = conn.cursor()
        cursor.execute(sql_commands)
        conn.commit()
        print("SQL commands executed successfully.")
    except Exception as e:
        print(f"Error executing SQL: {e}")
    finally:
        cursor.close()

# Função para extrair tabelas de 'localdb' e copiar para o novo banco
def transfer_tables_to_new_db():
    postgres_config_localdb = {
        "host": "localhost",
        "port": 5432,
        "database": "localdb",
        "user": "Admin",
        "password": "123456"
    }

    # Conexão com o banco de dados 'localdb'
    conn_localdb = psycopg2.connect(**postgres_config_localdb)
    conn_localdb.autocommit = True  # Para permitir operações DDL
    cursor_localdb = conn_localdb.cursor()

    # Obter os nomes das tabelas em 'localdb'
    cursor_localdb.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cursor_localdb.fetchall()
    print(f"Tables in localdb: {[table[0] for table in tables]}")

    conn_localdb.close()
    return tables

# Função para extrair dados das tabelas e salvar no novo banco de dados
def extract_and_save_tables():
    # Configurações de conexão para o novo banco de dados (via Docker)
    postgres_config_new_db = {
        "host": "localhost",
        "port": 5432,
        "database": "northwind",  # Nome do banco de dados conforme definido no Docker
        "user": "northwind_user",  # Nome do usuário conforme definido no Docker
        "password": "thewindisblowing"  # Senha conforme definida no Docker
    }

    # Estabelecendo conexão com o novo banco de dados
    conn_new_db = psycopg2.connect(**postgres_config_new_db)
    cursor_new_db = conn_new_db.cursor()

    # Obter a data atual
    execution_date = datetime.now().strftime("%Y-%m-%d")

    # Obter as tabelas de 'localdb' para transferir para o novo banco
    tables = transfer_tables_to_new_db()

    # Copiar os dados das tabelas para o novo banco e salvar os CSVs
    for table in tables:
        table_name = table[0]
        cursor_new_db.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS TABLE localdb.{table_name}")
        print(f"Table {table_name} copied to new database.")

        # Agora, extraímos os dados e salvamos como CSV
        cursor_new_db.execute(f"SELECT * FROM {table_name}")
        rows = cursor_new_db.fetchall()
        headers = [desc[0] for desc in cursor_new_db.description]
        data = [headers] + rows

        # Salvar os dados como CSV em /data/postgres/{table}/{date}/file.format
        save_to_local_disk(data, f"data/postgres/{table_name}/{execution_date}", f"{table_name}.csv")

        # Salvar também em /data/csv/{date}/file.format
        save_to_local_disk(data, f"data/csv/{execution_date}", f"{table_name}.csv")

    # Finalizando a conexão
    cursor_new_db.close()
    conn_new_db.close()

# Função para inicializar o Docker e configurar o PostgreSQL
def setup_docker():
    try:
        print("Starting Docker container from docker-compose.yml...")
        subprocess.run(["docker-compose", "-f", "docker-compose.yml", "up", "-d"], check=True)
        print("Docker container started.")
    except subprocess.CalledProcessError as e:
        print(f"Error starting Docker container: {e}")
        return

# Função principal para executar o processo
def main():
    print("Starting the process...")
    setup_docker()
    extract_and_save_tables()

if __name__ == "__main__":
    main()
