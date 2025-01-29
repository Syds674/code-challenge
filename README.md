# Desafio de Engenharia de Dados - TechIndicium

# Este repositório contém scripts para a realização de um desafio de engenharia de dados proposto pelo TechIndicium. O objetivo do desafio é extrair dados de fontes CSV e PostgreSQL e transferi-los para um banco de dados. O processo envolve a configuração de bancos de dados, a execução de scripts de extração e a organização dos dados extraídos em arquivos CSV.

# Estrutura do Repositório
# - extract_csv.py: Script para baixar e processar um arquivo CSV do GitHub.
# - extract_postgres.py: Script para baixar um arquivo SQL do GitHub, executar os comandos no PostgreSQL e extrair os dados das tabelas para CSV.
# - extract_and_transfer.py: Script para transferir os dados de um banco de dados localdb para o banco de dados northwind, e salvar os dados em arquivos CSV organizados por data e tabela.
# - setup.sh: Script para automatizar a instalação e configuração do ambiente, incluindo o Docker e o PostgreSQL.
# - docker-compose.yml: Arquivo para configurar o banco de dados northwind via Docker.

# Passo a Passo para Executar o Desafio

# 1. Clonar o Repositório
git clone https://github.com/Syds674/code-challenge.git
cd code-challenge

# 2. Executar o Script setup.sh (Opcional, se necessário configurar o ambiente)
chmod +x setup.sh
./setup.sh

# O script setup.sh irá instalar o Docker, Docker Compose, PostgreSQL e as dependências necessárias do Python.

# 3. Subir o Banco de Dados northwind com Docker
docker-compose up -d

# O comando acima irá iniciar os contêineres em segundo plano. Para verificar se os contêineres estão rodando corretamente, execute:
docker-compose ps

# Isso deverá exibir algo como:
# Name                Command              State           Ports
# -------------------------------------------------------------------
# northwind-db       docker-entrypoint.sh postgres    Up      0.0.0.0:5432->5432/tcp

# 4. Acessar o Banco de Dados northwind
# Para acessar o banco de dados northwind, você pode usar o psql ou um cliente gráfico como o DBeaver ou pgAdmin.

# Usando psql:
psql -h localhost -U postgres -d northwind

# A senha padrão para o usuário postgres é "postgres".

# Usando um cliente gráfico:
# Configure a conexão com as seguintes informações:
# - Host: localhost
# - Porta: 5432
# - Banco de dados: northwind
# - Usuário: postgres
# - Senha: postgres

# 5. Executar os Scripts de Extração de Dados
# Agora que o banco de dados está configurado e em execução, você pode rodar os scripts para extrair e transferir os dados.

# Para executar o script que transferirá os dados entre os bancos de dados localdb e northwind e salvará os dados em arquivos CSV, execute:

python3 Scripts/extract_and_transfer.py

# Esse script irá:
# - Extrair as tabelas do banco de dados "localdb"
# - Transferir os dados para o banco de dados "northwind"
# - Salvar os dados extraídos em arquivos CSV organizados por data e tabela

# 6. Parar os Contêineres do Docker
# Para parar os contêineres do Docker após a execução, execute:

docker-compose down
