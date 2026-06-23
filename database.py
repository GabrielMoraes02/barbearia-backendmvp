import sqlite3

def get_connection():
    # Conecta ao arquivo do banco (cria automaticamente se não existir)
    conn = sqlite3.connect("barbearia.db")
    conn.row_factory = sqlite3.Row  # permite acessar colunas pelo nome
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de barbeiros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS barbeiros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT
        )
    """)

    # Tabela de tipos de corte (catálogo de serviços)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tipos_corte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor REAL NOT NULL
        )
    """)

    # Tabela de atendimentos (um atendimento pode ter vários serviços)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cortes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barbeiro_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            forma_pagamento TEXT NOT NULL,
            FOREIGN KEY (barbeiro_id) REFERENCES barbeiros (id)
        )
    """)

    # Tabela de itens de cada atendimento (liga um corte a um ou mais tipos de serviço)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS corte_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            corte_id INTEGER NOT NULL,
            tipo_corte_id INTEGER NOT NULL,
            FOREIGN KEY (corte_id) REFERENCES cortes (id),
            FOREIGN KEY (tipo_corte_id) REFERENCES tipos_corte (id)
        )
    """)

    # Tabela de agendamentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barbeiro_id INTEGER NOT NULL,
            tipo_corte_id INTEGER,
            nome_cliente TEXT NOT NULL,
            data_hora TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'agendado',
            FOREIGN KEY (barbeiro_id) REFERENCES barbeiros (id),
            FOREIGN KEY (tipo_corte_id) REFERENCES tipos_corte (id)
        )
    """)

    conn.commit()
    conn.close()