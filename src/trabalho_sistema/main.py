from pathlib import Path
import sqlite3
import csv
from flask import Flask, jsonify, request

CSV_PATH = Path(__file__).with_name("logs_acesso.csv")

app = Flask(__name__)

DB_PATH = (
    Path.home()
    / "OneDrive"
    / "Área de Trabalho"
    / "trabalho_sistema"
    / "acess_control.db"
)


def conectar():
  # Garante que a URI use o formato correto para o SQLite
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
        colunas = conn.execute(f'PRAGMA table_info("{tabela}")').fetchall()

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

    return jsonify([dict(pessoa) for pessoa in pessoas])

  except sqlite3.Error:
    app.logger.exception("Erro ao consultar pessoas")
    return jsonify({"erro": "Falha ao consultar pessoas"}), 500


@app.post("/api/logs")
def receber_log():
  dados = request.get_json(silent=True)

  if not isinstance(dados, dict):
    return jsonify({"erro": "JSON inválido"}), 400

  campos = [
      "data_hora",
      "tag_uid",
      "nome",
      "evento",
      "resultado",
      "mensagem",
  ]

  if any(campo not in dados for campo in campos):
    return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

  try:
    # Garante que a pasta do arquivo CSV existe antes de tentar abrir
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

    arquivo_novo = not CSV_PATH.exists()

    with CSV_PATH.open("a", newline="", encoding="utf-8-sig") as arquivo:
      escritor = csv.DictWriter(
          arquivo,
          fieldnames=campos,
          extrasaction="ignore",
      )

      if arquivo_novo or CSV_PATH.stat().st_size == 0:
        escritor.writeheader()

      escritor.writerow({campo: dados[campo] for campo in campos})

    return jsonify({"status": "ok", "salvo": True}), 201

  except OSError:
    app.logger.exception("Erro ao salvar log CSV")
    return jsonify({"erro": "Falha ao salvar CSV"}), 500


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=False)