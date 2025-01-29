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

def write_to_postgres(data, table_name):
    postgres_config = {
        "host": "localhost",
        "port": 5432,
        "database": "localdb",
        "user": "Admin",
        "password": "123456"
    }

    conn = None  # Inicialize a variável conn fora do bloco try
    try:
        conn = psycopg2.connect(**postgres_config)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        headers = data[0]
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{header} TEXT' for header in headers])})")

        # Insert data
        for row in data[1:]:
            placeholders = ', '.join(['%s'] * len(row))
            cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row)

        conn.commit()
        print(f"Data written to PostgreSQL table {table_name}")

    except Exception as e:
        print(f"Error writing to PostgreSQL: {e}")

    finally:
        if conn:  # Verifique se conn foi definida antes de tentar fechar
            cursor.close()
            conn.close()

def extract_csv():
    # URL correto para baixar o arquivo CSV do GitHub
    csv_url = "https://raw.githubusercontent.com/techindicium/code-challenge/main/data/order_details.csv"
    execution_date = datetime.now().strftime("%Y-%m-%d")
    local_path = f"data/csv/{execution_date}"
    file_name = "order_details.csv"  # Alterando para o nome real do arquivo

    # Download and process the CSV file
    response = requests.get(csv_url)
    response.raise_for_status()

    rows = response.text.splitlines()
    csv_data = list(csv.reader(rows))

    save_to_local_disk(csv_data, local_path, file_name)

    # Usar o nome real do arquivo (sem a extensão) como o nome da tabela
    table_name = file_name.replace('.csv', '')  # Remove a extensão .csv
    write_to_postgres(csv_data, table_name)

def main():
    print("Starting CSV extraction...")
    extract_csv()

if __name__ == "__main__":
    main()
