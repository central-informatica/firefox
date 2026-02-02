import sqlite3

def getDb():
    DB_PATH = "./storage/db/meu_banco.db"
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS acesso (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario TEXT NOT NULL,
        token TEXT NOT NULL,
        ativo INTEGER not null
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS certificados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario TEXT NOT NULL,
        nome_arquivo TEXT NOT NULL,
        cert_id TEXT NOT NULL,
        encrypted TEXT NOT NULL,
        secret TEXT NOT NULL
    )
    """)
    return conexao


