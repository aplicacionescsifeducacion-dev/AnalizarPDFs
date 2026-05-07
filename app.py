from flask import Flask, request, jsonify
import fitz
import re
from collections import defaultdict
from flask_cors import CORS

app = Flask(__name__)

# 🔥 CORS CORRECTO (incluye API-KEY)
CORS(app, resources={r"/*": {
    "origins": "*",
    "allow_headers": ["Content-Type", "API-KEY"],
    "methods": ["GET", "POST", "OPTIONS"]
}})

REGEX_ESPECIALIDAD = re.compile(r"ESPECIALIDAD\s*:\s*(.+)", re.IGNORECASE)
REGEX_SI = re.compile(r"\b(SI|S|SÍ)\b", re.IGNORECASE)

@app.route("/")
def index():
    return jsonify({"status": "API funcionando"})

@app.route("/analizar", methods=["POST", "OPTIONS"])
def analizar():

    # 🔥 Preflight CORS obligatorio
    if request.method == "OPTIONS":
        return "", 204

    try:
        # 🔐 API KEY CHECK
        if request.headers.get("API-KEY") != "12345":
            return jsonify({"error": "No autorizado"}), 403

        # 📄 validar archivo
        if "pdf" not in request.files:
            return jsonify({"error": "No PDF recibido"}), 400

        archivo = request.files["pdf"]
        pdf_bytes = archivo.read()

        resultados = defaultdict(lambda: {"total": 0, "admitidos": 0})
        especialidad_actual = None

        # 📊 leer PDF
        with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf:
            for pagina in pdf:
                texto = pagina.get_text()

                if not texto:
                    continue

                for linea in texto.split("\n"):
                    linea = linea.strip()

                    # detectar especialidad
                    match = REGEX_ESPECIALIDAD.search(linea)
                    if match:
                        especialidad_actual = match.group(1).strip()
                        continue

                    # detectar SI
                    if REGEX_SI.search(linea):
                        if especialidad_actual:
                            resultados[especialidad_actual]["total"] += 1
                            resultados[especialidad_actual]["admitidos"] += 1

        return jsonify(resultados)

    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500


# 🔥 evitar error favicon (opcional)
@app.route("/favicon.ico")
def favicon():
    return "", 204


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
