# app.py
import os
import sqlite3
from flask import Flask, request, g, render_template, redirect, url_for, send_file, jsonify, flash
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from werkzeug.utils import secure_filename

# Configurações
DB_PATH = "database.db"
UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"
ALLOWED_EXTENSIONS = {"csv"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = "troque_para_uma_chave_secreta"  # substituir em produção
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

# ---------------------------
# Banco de dados
# ---------------------------
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    from pathlib import Path
    if not Path(DB_PATH).exists():
        with open("schema.sql", "r") as f:
            sql = f.read()
        conn = sqlite3.connect(DB_PATH)
        conn.executescript(sql)
        conn.commit()
        conn.close()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

# ---------------------------
# Utilitários
# ---------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------------------
# Rotas
# ---------------------------
@app.route("/")
def index():
    db = get_db()
    cur = db.execute("SELECT DISTINCT municipio FROM hemograma ORDER BY municipio")
    municipios = [r["municipio"] for r in cur.fetchall()]
    cur = db.execute("SELECT COUNT(*) as c FROM alerts WHERE date(data_alerta) >= date('now','-30 days')")
    alert_count = cur.fetchone()["c"]
    return render_template("index.html", municipios=municipios, alert_count=alert_count)

@app.route("/upload", methods=["GET","POST"])
def upload():
    if request.method == "POST":
        if 'file' not in request.files:
            flash("Nenhum arquivo enviado", "error")
            return redirect(request.url)
        f = request.files['file']
        if f.filename == '':
            flash("Nome do arquivo vazio", "error")
            return redirect(request.url)
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(path)
            try:
                ingest_csv(path)
                flash("Arquivo processado com sucesso", "success")
            except Exception as e:
                flash(f"Erro ao processar arquivo: {e}", "error")
            return redirect(url_for('index'))
        else:
            flash("Formato inválido. Envie CSV.", "error")
            return redirect(request.url)
    return render_template("upload.html")

def ingest_csv(path):
    df = pd.read_csv(path, parse_dates=["data_coleta"])
    # normalize columns
    df.columns = [c.strip().lower() for c in df.columns]
    # required columns check
    required = {"paciente_id","municipio","data_coleta","plaquetas"}
    if not required.issubset(set(df.columns)):
        raise ValueError(f"CSV precisa conter colunas: {required}")
    df = df.fillna("")
    conn = get_db()
    cur = conn.cursor()
    for _, row in df.iterrows():
        # ensure types
        date_str = pd.to_datetime(row["data_coleta"]).strftime("%Y-%m-%d")
        plaquetas = int(row["plaquetas"])
        cur.execute("""
            INSERT INTO hemograma (paciente_id, municipio, data_coleta, plaquetas, faixa_etaria, sexo)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (str(row.get("paciente_id","")), str(row.get("municipio","")), date_str, plaquetas, str(row.get("faixa_etaria","")), str(row.get("sexo",""))))
    conn.commit()

@app.route("/api/metrics")
def api_metrics():
    start = request.args.get("start")
    end = request.args.get("end")
    db = get_db()
    params = []
    q = "SELECT municipio, data_coleta, AVG(plaquetas) as mean_plaquetas FROM hemograma"
    if start and end:
        q += " WHERE date(data_coleta) BETWEEN ? AND ?"
        params = [start, end]
    q += " GROUP BY municipio, data_coleta ORDER BY municipio, data_coleta"
    rows = db.execute(q, params).fetchall()
    data = {}
    for r in rows:
        m = r["municipio"]
        data.setdefault(m, []).append({"date": r["data_coleta"], "mean": r["mean_plaquetas"]})
    return jsonify(data)

@app.route("/api/alerts")
def api_alerts():
    db = get_db()
    rows = db.execute("SELECT municipio, data_alerta, tipo, valor, descricao FROM alerts ORDER BY data_alerta DESC LIMIT 200").fetchall()
    res = [{"municipio":r["municipio"], "date":r["data_alerta"], "tipo":r["tipo"], "valor":r["valor"], "descricao":r["descricao"]} for r in rows]
    return jsonify(res)

def detect_alerts(persist=True):
    # detection rules:
    # - absolute threshold: mean < 100000
    # - relative drop: last_mean < moving_avg(prev 14 days) * 0.8
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT municipio, data_coleta, AVG(plaquetas) as mean_plaquetas FROM hemograma GROUP BY municipio, data_coleta", conn, parse_dates=["data_coleta"])
    alerts = []
    if df.empty:
        conn.close()
        return alerts
    municipios = df["municipio"].unique()
    for m in municipios:
        sdf = df[df["municipio"]==m].sort_values("data_coleta").reset_index(drop=True)
        if len(sdf) < 3:
            continue
        # compute rolling mean (previous window)
        sdf["ma14"] = sdf["mean_plaquetas"].rolling(window=14, min_periods=3).mean()
        # examine last N days rows where ma14 not NaN
        for idx, row in sdf.iterrows():
            last_mean = row["mean_plaquetas"]
            ma = row["ma14"]
            date = row["data_coleta"].strftime("%Y-%m-%d")
            if last_mean < 100000:
                alerts.append({"municipio":m, "date":date, "tipo":"limiar", "valor":float(last_mean), "descricao":"Média abaixo de 100000"})
            elif pd.notna(ma) and (last_mean < 0.8 * ma):
                rel = (ma - last_mean)/ma
                alerts.append({"municipio":m, "date":date, "tipo":"queda_relativa", "valor":float(rel), "descricao":f"Queda relativa {rel:.2f} > 0.2"})
    if persist and alerts:
        cur = conn.cursor()
        for a in alerts:
            cur.execute("""
                INSERT INTO alerts (municipio, data_alerta, tipo, valor, descricao)
                VALUES (?, ?, ?, ?, ?)
            """, (a["municipio"], a["date"], a["tipo"], a["valor"], a["descricao"]))
        conn.commit()
    conn.close()
    return alerts

@app.route("/run_detection", methods=["POST"])
def run_detection_route():
    alerts = detect_alerts(persist=True)
    registrar_log(f"Detecção executada – {len(alerts)} alertas gerados")
    return jsonify({"ok": True, "alerts_generated": len(alerts)})

@app.route("/logs")
def ver_logs():
    db = get_db()
    rows = db.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 50").fetchall()
    logs = [{"acao": r["acao"], "data": r["data_hora"]} for r in rows]
    return render_template("logs.html", logs=logs)


@app.route("/plot/<municipio>")
def plot_municipio(municipio):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT data_coleta, AVG(plaquetas) as mean_plaquetas FROM hemograma WHERE municipio=? GROUP BY data_coleta ORDER BY data_coleta", conn, params=(municipio,))
    conn.close()
    if df.empty:
        return "No data for this municipio", 404
    df['data_coleta'] = pd.to_datetime(df['data_coleta'])
    plt.figure(figsize=(8,3))
    plt.plot(df['data_coleta'], df['mean_plaquetas'], marker='o', linewidth=1)
    plt.title(f"Média de plaquetas - {municipio}")
    plt.ylabel("Plaquetas (média)")
    plt.xlabel("Data")
    plt.tight_layout()
    path = os.path.join(app.config['STATIC_FOLDER'], f"plot_{municipio}.png")
    plt.savefig(path)
    plt.close()
    return send_file(path, mimetype='image/png')

def registrar_log(acao):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO logs (acao, data_hora) VALUES (?, datetime('now','localtime'))",
        (acao,)
    )
    conn.commit()
    conn.close()

# ---------------------------
# Inicialização
# ---------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
