import os
import csv
import psycopg2
from datetime import datetime
import requests

def create_directory(path):
    os.makedirs(path, exist_ok=True)

def save_to_local_disk(data, path, file_name):
    create_directory(path)
    file_path = os.path.join(path, file_name)
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    print(f"Data saved to {file_path}")

def clean_sql_commands(sql_commands):
    """Remove linhas problemáticas e metadados inválidos."""
    lines = sql_commands.split("\n")
    cleaned_lines = []
    for line in lines:
        # Ignorar metadados e linhas inválidas
        if line.strip().startswith(("Type:", "Schema:", "Owner:", "--")) or not line.strip():
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def execute_sql_file(conn, sql_file_path):
    try:
        cursor = conn.cursor()
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_commands = file.read()

        # Limpar comandos SQL
        sql_commands = clean_sql_commands(sql_commands)

        # Separar comandos SQL
        commands = [cmd.strip() for cmd in sql_commands.split(";") if cmd.strip()]

        if not commands:
            print("Error: No valid SQL commands found in the file.")
            return

        for command in commands:
            try:
                cursor.execute(command)
            except Exception as e:
                print(f"Error executing command: {command[:50]}... - {e}")

        conn.commit()
        print(f"SQL file {sql_file_path} executed successfully.")

    except Exception as e:
        print(f"Error executing SQL file: {e}")

    finally:
        if cursor:
            cursor.close()

def extract_postgres():
    postgres_config = {
        "host": "localhost",
        "port": 5432,
        "database": "localdb",  # Conectando ao banco 'localdb'
        "user": "Admin",
        "password": "123456"
    }

    execution_date = datetime.now().strftime("%Y-%m-%d")
    sql_url = "https://raw.githubusercontent.com/techindicium/code-challenge/main/data/northwind.sql"
    sql_file_path = "northwind.sql"

    # Baixar o arquivo SQL do GitHub
    try:
        response = requests.get(sql_url)
        response.raise_for_status()
        with open(sql_file_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        print(f"SQL file downloaded and saved to {sql_file_path}.")
    except Exception as e:
        print(f"Error downloading SQL file: {e}")
        return

    conn = None
    try:
        conn = psycopg2.connect(**postgres_config)
        conn.autocommit = True  # Permite execução de comandos DDL sem necessidade de commit

        # Criar e popular o banco
        execute_sql_file(conn, sql_file_path)

        # Verificar tabelas criadas
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()

        if not tables:
            print("No tables found in the database. Check the SQL execution.")
            return

        # Confirmar tabelas criadas no banco de dados
        print(f"The following tables have been created in the database '{postgres_config['database']}':")
        for table in tables:
            print(f"- {table[0]}")

        # Extrair dados das tabelas e salvar em arquivos CSV
        for table in tables:
            table_name = table[0]
            table_query = f"SELECT * FROM {table_name}"
            cursor.execute(table_query)
            rows = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description]
            
            data = [headers] + rows
            save_to_local_disk(data, f"data/postgres/{table_name}/{execution_date}", f"{table_name}.csv")
            print(f"Data from table {table_name} saved to disk.")

        # Excluir o banco de dados após extração
        print(f"Dropping the 'northwind' database to clean up...")
        cursor.execute("DROP DATABASE IF EXISTS northwind")

        # Remover o arquivo SQL após a execução
        if os.path.exists(sql_file_path):
            os.remove(sql_file_path)
            print(f"File {sql_file_path} removed after execution.")

    except Exception as e:
        print(f"Error extracting PostgreSQL data: {e}")

    finally:
        if conn:
            cursor.close()
            conn.close()

def main():
    print("Starting PostgreSQL extraction...")
    extract_postgres()

if __name__ == "__main__":
    main()
