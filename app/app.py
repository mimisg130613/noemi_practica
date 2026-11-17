import os, time
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )

def init_db():
    for _ in range(20):
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS notas (id SERIAL PRIMARY KEY, texto TEXT NOT NULL)")
            conn.commit()
            conn.close()
            return
        except psycopg2.OperationalError:
            time.sleep(2)
    raise RuntimeError("No se pudo conectar a la base de datos")

@app.route("/")
def listar():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, texto FROM notas ORDER BY id")
    filas = [{"id": r[0], "texto": r[1]} for r in cur.fetchall()]
    conn.close()
    return jsonify(filas)

@app.route("/notas", methods=["POST"])
def crear():
    texto = request.get_json()["texto"]
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO notas (texto) VALUES (%s) RETURNING id", (texto,))
    nuevo_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return jsonify({"id": nuevo_id, "texto": texto}), 201

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
