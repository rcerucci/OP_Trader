#!/usr/bin/env bash

set -e  # Para imediatamente ao primeiro erro

# Utilitário para saída colorida
error() { echo -e "\033[0;31m[ERRO]\033[0m $1"; exit 1; }
info()  { echo -e "\033[0;32m[INFO]\033[0m $1"; }
warn()  { echo -e "\033[0;33m[WARN]\033[0m $1"; }

# Se pyenv disponível, troca Python
if command -v pyenv >/dev/null 2>&1; then
    info "Alterando Python com pyenv para 3.10.17"
    pyenv global 3.10.17
fi

python --version

# Atualiza pip
python -m pip install --upgrade pip

# Cria e ativa venv local
if [ ! -d ".venv" ]; then
    info "Criando ambiente virtual .venv"
    python -m venv .venv
fi

source .venv/bin/activate

# Garante pip atualizado
pip install --upgrade pip

# Instala todas as dependências
info "Instalando requirements.txt"
pip install -r requirements.txt || error "Falha na instalação de requirements.txt!"

# Instala pytest explicitamente (garantia extra)
pip install pytest

# Teste se pacotes principais estão ok (diagnóstico)
python -c "import numpy, pandas, gymnasium, yaml" || error "Algum pacote essencial não foi instalado!"

# Cria diretório logs e .gitkeep
mkdir -p logs
touch logs/.gitkeep