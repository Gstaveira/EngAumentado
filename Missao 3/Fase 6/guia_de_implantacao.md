Guia de Implantação – Sistema de Monitoramento de Hemogramas
1. Visão Geral

O Sistema de Monitoramento de Hemogramas é um aplicativo desenvolvido em Flask que permite o envio, processamento e análise automática de arquivos de hemograma no formato CSV, armazenando resultados em um banco SQLite e exibindo classificações de risco ao usuário.

Este documento descreve todo o processo de implantação, desde os requisitos do ambiente até a execução final do servidor, garantindo que o sistema seja corretamente configurado e disponibilizado em ambiente real.

2. Requisitos do Ambiente
Requisitos de Software

Python 3.10 ou superior

Pip 23+

SQLite 3

Sistema Operacional: Windows, Linux ou MacOS

Git (opcional, para atualização por versionamento)

Requisitos de Hardware

Mínimo:

2 GB de RAM

1 CPU

200 MB de espaço em disco

Recomendado:

4 GB de RAM

2 CPUs

Portas

A aplicação Flask utiliza por padrão a porta 8000:

http://localhost:8000

3. Preparação do Ambiente
3.1 Obtendo o Projeto

Clone o repositório oficial:

git clone https://github.com/Gstaveira/EngAumentado


Acesse o diretório da aplicação:

cd EngAumentado/monitoramento-hemogramas

3.2 Criando o Ambiente Virtual

Para isolar dependências:

Windows

python -m venv venv
venv\Scripts\activate


Linux/Mac

python3 -m venv venv
source venv/bin/activate

3.3 Instalando Dependências

Com o ambiente ativo:

pip install -r requirements.txt


As dependências incluem:

Flask (servidor web)

Werkzeug (manipulação segura de uploads)

Pandas (processamento de CSV)

Outros itens necessários ao fluxo

4. Configuração do Banco de Dados

O sistema utiliza SQLite para armazenamento local dos resultados de análises.

Verifique se o arquivo database.db existe. Caso não exista, crie-o usando o schema oficial:

sqlite3 database.db < schema.sql


O schema define:

Tabela de resultados de hemogramas

Campos de risco, data da análise e métricas essenciais

5. Execução do Sistema

A forma mais simples de executar o aplicativo é via Flask CLI:

export FLASK_APP=app.py     (Linux/Mac)
set FLASK_APP=app.py        (Windows)

flask run --host=0.0.0.0 --port=8000


Ou utilize o script de deploy automático (disponível no projeto):

./deploy.sh


Este script:

Ativa o ambiente virtual

Instala dependências

Inicializa o banco, se necessário

Inicia o servidor Flask

6. Acessando o Sistema

Após a execução, abra o navegador em:

http://localhost:8000


Você poderá:

Enviar arquivos CSV de hemograma

Visualizar análises automáticas

Acessar histórico de envios

Consultar classificações de risco

7. Estrutura de Pastas Após Implantação
monitoramento-hemogramas/
 ├── app.py                  ← Aplicação principal Flask
 ├── database.db             ← Banco SQLite
 ├── schema.sql              ← Script de criação do banco
 ├── uploads/                ← Arquivos enviados pelos usuários
 ├── static/                 ← CSS, JS, imagens
 ├── templates/              ← HTML (Flask Jinja2)
 ├── generate_synthetic.py   ← Gerador de dados sintéticos
 ├── hemograma_sintetico.csv ← CSV de exemplo
 ├── requirements.txt        ← Dependências
 ├── deploy.sh               ← Script automático de implantação
 └── venv/                   ← Ambiente virtual Python

8. Boas Práticas de Produção
Segurança

Configure SECRET_KEY em arquivo externo (ex: config.env)

Limite o tamanho de uploads

Valide colunas obrigatórias nos CSVs

Logs

Direcione logs do Flask para arquivo:

flask run > flask.log 2>&1

Testes antes do deploy

Execute sempre:

pytest --cov=.

9. Resolução de Problemas Comuns
Problema	Possível causa	Solução
Erro ao iniciar o Flask	Dependências faltando	pip install -r requirements.txt
Banco não encontrado	database.db ausente	sqlite3 database.db < schema.sql
Upload falhou	CSV inválido	Verificar colunas: hemacias, leucocitos, plaquetas
Porta ocupada	Outro app rodando	Alterar porta: flask run --port=8080
10. Conclusão

Com esse processo de implantação, o Sistema de Monitoramento de Hemogramas pode ser configurado, executado e disponibilizado de forma consistente e segura em qualquer ambiente local ou servidor. A documentação garante rastreabilidade total do processo, facilitando manutenção, auditoria e suporte técnico.
