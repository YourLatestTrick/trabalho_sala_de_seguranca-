from pathlib import Path
import sqlite3

from flask import Flask, jsonify

app = Flask(__name__)

DB_PATH = (
    Path.home()
    / "OneDrive"
    / "Área de Trabalho"
    / "trabalho_sistema"
    / "acess_control.db"
)


def conectar():
    uri = DB_PATH.resolve().as_uri() + "?mode=ro"
    return sqlite3.connect(uri, uri=True)


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "banco_existe": DB_PATH.is_file(),
    })


@app.get("/api/schema")
def schema():
    if not DB_PATH.is_file():
        return jsonify({"erro": "Banco não encontrado"}), 404

    try:
        with conectar() as conn:
            tabelas = conn.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """).fetchall()

            resultado = {}

            for (tabela,) in tabelas:
                colunas = conn.execute(
                    f'PRAGMA table_info("{tabela}")'
                ).fetchall()

                resultado[tabela] = [
                    {
                        "nome": coluna[1],
                        "tipo": coluna[2],
                    }
                    for coluna in colunas
                ]

        return jsonify(resultado)

    except sqlite3.Error:
        app.logger.exception("Erro ao consultar o banco")
        return jsonify({"erro": "Falha ao consultar o banco"}), 500

@app.get("/api/pessoas")
def listar_pessoas():
    if not DB_PATH.is_file():
        return jsonify({"erro": "Banco não encontrado"}), 404

    try:
        with conectar() as conn:
            conn.row_factory = sqlite3.Row
            pessoas = conn.execute("""
                SELECT id, nome, rfid, cargo, acesso_sala, status
                FROM pessoas
            """).fetchall()

        return jsonify([
            dict(pessoa) for pessoa in pessoas
        ])

    except sqlite3.Error:
        app.logger.exception("Erro ao consultar pessoas")
        return jsonify({"erro": "Falha ao consultar pessoas"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)