import sqlite3
import uuid

def initialize_database():
    connection = sqlite3.connect("acess_control.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pessoas (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            rfid TEXT UNIQUE NOT NULL,
            cargo TEXT NOT NULL,
            acesso_sala TEXT CHECK(acesso_sala IN ('sim', 'nao')) NOT NULL,
            status TEXT CHECK(status IN ('ativo', 'inativo')) NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM pessoas")
    total_rows = cursor.fetchone()[0]

    if total_rows == 0:
        initial_users = [
            (
                str(uuid.uuid4()),
                "Pedro Silva",
                "962185903074",
                "Técnico de Infraestrutura",
                "sim",
                "ativo",
            ),
            (
                str(uuid.uuid4()),
                "Carlo Edoardo",
                "701044494601",
                "Desenvolvedor Python Sênior",
                "sim",
                "ativo",
            ),
            (
                str(uuid.uuid4()),
                "Miguel Alencar",
                "632092037175",
                "Recepcionista",
                "nao",
                "ativo",
            ),
            (
                str(uuid.uuid4()),
                "Sophia Bonita",
                "427066982110",
                "Gerente",
                "nao",
                "ativo",
            ),
        ]

        cursor.executemany(
            """
                INSERT INTO pessoas (id, nome, rfid, cargo, acesso_sala, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            initial_users,
        )

        connection.commit()
        print("Banco de dados criado e dados inseridos")
    else:
        print("Banco de dados já foi inicializado")

    connection.close()
