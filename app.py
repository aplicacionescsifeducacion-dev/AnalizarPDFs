from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import re
import tempfile
import os

app = Flask(__name__)

# 🔥 CORS correcto (obligatorio para Netlify)
CORS(app, resources={r"/*": {
    "origins": "*",
    "allow_headers": ["Content-Type"],
    "methods": ["GET", "POST", "OPTIONS"]
}})

regex_dni = re.compile(r"\*{4}\d{3,4}\*")
VALORES_ADMITIDO = {"04"}

# 🔥 endpoint correcto
@app.route("/analizar", methods=["POST", "OPTIONS"])
def analizar():

    # 🔵 Preflight CORS (IMPORTANTE)
    if request.method == "OPTIONS":
        return "", 204

    # 🔴 bloquear GET (evita 405 confuso)
    if request.method != "POST":
        return jsonify({"error": "Método no permitido"}), 405

    try:
        if "pdf" not in request.files:
            return jsonify({"error": "No se envió PDF"}), 400

        pdf_file = request.files["pdf"]

        # 🔥 archivo temporal seguro
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            pdf_file.save(temp.name)
            path = temp.name

        resultados = {
            "Especialidad": {
                "total": 0,
                "admitidos": 0
            }
        }

        # 🔥 lectura PDF
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                words = page.extract_words()
                filas = {}

                for w in words:
                    y = round(w["top"], 0)
                    filas.setdefault(y, []).append(w)

                for fila in filas.values():
                    texto = [w["text"] for w in fila]

                    dnis = [t for t in texto if regex_dni.match(t)]
                    if not dnis:
                        continue

                    resultados["Especialidad"]["total"] += len(dnis)

                    tipos = [t for t in texto if t in VALORES_ADMITIDO]
                    resultados["Especialidad"]["admitidos"] += len(tipos)

        os.remove(path)

        return jsonify(resultados)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔥 evita error favicon (404)
@app.route("/favicon.ico")
def favicon():
    return "", 204


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
