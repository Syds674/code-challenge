#!/bin/bash

set -e # Terminar o script imediatamente se um comando falhar
set -o pipefail # Propagar falhas em pipes

# Função para exibir mensagens
log() {
    echo "****** $1"
}

# Atualizar e atualizar listas de pacotes
log "Atualizando lista de pacotes..."
sudo apt update && sudo apt upgrade -y
log "Lista de pacotes atualizada com sucesso!"

# Instalar dependências básicas (incluindo curl)
log "Instalando dependências básicas (curl, etc.)..."
sudo apt install -y curl software-properties-common
log "Dependências básicas instaladas com sucesso!"

# Instalar PostgreSQL
log "Instalando PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib
log "PostgreSQL instalado com sucesso!"

log "Iniciando e habilitando o serviço PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

log "Verificando status do serviço PostgreSQL..."
if sudo systemctl is-active --quiet postgresql; then
    log "Serviço PostgreSQL ativo!"
else
    log "Erro: Serviço PostgreSQL inativo."
    exit 1
fi

# Verificar se o banco de dados LocalDB já existe
log "Verificando se o banco de dados LocalDB já existe..."
DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='localdb';")

if [ "$DB_EXISTS" == "1" ]; then
    log "Banco de dados LocalDB já existe. Continuando..."
else
    log "Criando banco de dados LocalDB..."
    sudo -u postgres psql -c "CREATE DATABASE localdb;"
    log "Banco de dados LocalDB criado com sucesso!"
fi

# Instalar Python 3.9
log "Instalando Python 3.9..."
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.9 python3.9-distutils
log "Python 3.9 instalado com sucesso!"

log "Verificando versão do Python..."
python3.9 --version || (log "Erro: Python 3.9 não foi instalado corretamente."; exit 1)

log "Instalando pip para Python 3.9..."
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.9 get-pip.py
rm get-pip.py
log "pip instalado com sucesso!"

log "Verificando versão do pip..."
pip3 --version || (log "Erro: pip não foi instalado corretamente."; exit 1)

# Instalar Docker
log "Atualizando lista de pacotes para Docker..."
sudo apt update && sudo apt upgrade -y
log "Lista de pacotes atualizada!"

log "Instalando pré-requisitos do Docker..."
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

log "Adicionando chave GPG do Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

log "Adicionando repositório do Docker..."
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

log "Atualizando lista de pacotes novamente..."
sudo apt update

log "Instalando Docker..."
sudo apt install -y docker-ce
log "Docker instalado com sucesso!"

log "Verificando versão do Docker..."
sudo docker --version || (log "Erro: Docker não foi instalado corretamente."; exit 1)

log "Adicionando usuário ao grupo Docker..."
sudo usermod -aG docker $USER
log "Usuário adicionado ao grupo Docker com sucesso! Reinicie a sessão para aplicar alterações."

# Instalar Airflow seguindo as instruções oficiais
log "Instalando dependências do Airflow..."
sudo apt install -y libpq-dev python3.9-dev

log "Criando ambiente virtual para Airflow..."
python3.9 -m venv airflow_env
source airflow_env/bin/activate

log "Atualizando pip no ambiente virtual..."
pip install --upgrade pip

log "Instalando Apache Airflow com PostgreSQL support..."
AIRFLOW_VERSION=2.6.3
PYTHON_VERSION="$(python3.9 --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
pip install "apache-airflow[postgres]==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

# Corrigir conflitos de dependências com versões específicas 
log "Instalando versões compatíveis de SQLAlchemy e Packaging..." 
pip cache purge # Limpa o cache do pip 
pip install --force-reinstall "sqlalchemy==1.4.43" "packaging==21.3"

log "Configurando o banco de dados do Airflow..."
export AIRFLOW_HOME=$(pwd)/airflow_home
airflow db init

log "Criando usuário administrador do Airflow..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname Admin \
    --role Admin \
    --email admin@example.com \
    --password admin

log "Iniciando servidor web do Airflow..."
airflow webserver -D

log "Iniciando agendador do Airflow..."
airflow scheduler -D

log "Airflow configurado! Acesse http://localhost:8080 para usar."

# Instalar Meltano
log "Instalando Meltano..."
pip install meltano

log "Inicializando projeto Meltano..."
meltano init Indicium_Project
if [ $? -eq 0 ]; then
    log "Projeto Meltano inicializado com sucesso!"
else
    log "Erro: Falha ao inicializar o projeto Meltano."
    exit 1
fi

log "Instalação concluída! Projeto Meltano inicializado com sucesso."
