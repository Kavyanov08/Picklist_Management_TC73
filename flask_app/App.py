from flask import Flask, request, jsonify, render_template
import pandas as pd
import psycopg2

app = Flask(__name__)

# ── Simple reconnect helper (no pooling needed for single device) ─────
def get_db():
    return psycopg2.connect(
        host="localhost",
        user="postgres",
        password="postgre@123",
        dbname="picklist_db",
        port="5432"
    )

# ── Routes ─────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['file']
        df = pd.read_excel(file)

        db = get_db()
        cursor = db.cursor()

        cursor.execute("DELETE FROM picklist")

        for val in df['Picklist']:
            cursor.execute("INSERT INTO picklist(code) VALUES(%s)", (str(val),))

        db.commit()
        cursor.close()
        db.close()

        return jsonify({"status": "success"})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
@app.route('/all_picklist')
def all_picklist():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT code, status FROM picklist")
    rows = cursor.fetchall()
    data = [{"code": r[0], "status": r[1]} for r in rows]
    cursor.close()
    db.close()
    return jsonify(data)

@app.route('/picklist')
def picklist():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT code FROM picklist WHERE status='pending'")
    rows = cursor.fetchall()
    data = [row[0] for row in rows]
    cursor.close()
    db.close()
    return jsonify(data)
@app.route('/update', methods=['POST'])
def update():
    code = request.form.get('code')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE picklist SET status='picked' WHERE code=%s", (code,))
    db.commit()
    cursor.close()
    db.close()
    return "updated"

# ── Run on ALL network interfaces so TC73 can reach it ────────────────
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
