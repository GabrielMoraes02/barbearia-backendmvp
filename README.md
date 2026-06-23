# Barbearia API

API REST para gestão de uma barbearia: cadastro de barbeiros, catálogo de tipos de corte, registro de atendimentos (com múltiplos serviços por atendimento), agendamentos com consulta de disponibilidade, e relatórios de faturamento.

Projeto desenvolvido como MVP para a disciplina de Desenvolvimento Full Stack Básico, aplicando os conceitos de arquitetura REST propostos por Roy Fielding.

## Tecnologias

- Python 3
- Flask
- SQLite
- Flasgger (documentação Swagger/OpenAPI)
- Flask-CORS

## Funcionalidades

- Cadastro, listagem e remoção de barbeiros
- Cadastro, listagem e remoção de tipos de corte (catálogo de serviços com valores)
- Registro de atendimentos com um ou mais serviços, com cálculo automático do valor total
- Agendamentos com consulta de disponibilidade de horários (08h às 20h, intervalos de 1 hora)
- Relatório de faturamento por barbeiro em um intervalo de datas
- Ranking de barbeiros por faturamento total

## Instalação

### Pré-requisitos

- Python 3.10 ou superior instalado

### Passo a passo

1. Clone este repositório:

git clone <url-do-repositorio>

cd barbearia-backend

2. Crie um ambiente virtual:

python -m venv venv

3. Ative o ambiente virtual:

No Windows:
venv\Scripts\activate

4. Instale as dependências:

pip install flask flask-cors flasgger

5. Execute o servidor:

python app.py


6. A API estará disponível em `http://127.0.0.1:5000`

## Documentação da API

Com o servidor rodando, acesse a documentação interativa (Swagger) em:

http://127.0.0.1:5000/apidocs

## Estrutura do projeto

barbearia-backend/

├── app.py

├── database.py

├── routes_barbeiros.py

├── routes_tipos_corte.py

├── routes_cortes.py

├── routes_agendamentos.py

├── routes_relatorios.py

└── README.md