#!/bin/bash

echo "==== DEPLOY DO SISTEMA DE MONITORAMENTO DE HEMOGRAMAS ===="

# 1. Ativa ambiente
echo "Ativando ambiente virtual..."
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate

# 2. Instala requisitos
echo "Instalando dependências..."
pip install -r requirements.txt

# 3. Verifica banco
if [ ! -f "database.db" ]; then
    echo "Inicializando banco SQLite..."
    sqlite3 database.db < schema.sql
fi

# 4. Inicia aplicação
echo "Iniciando servidor Flask..."
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=8000

