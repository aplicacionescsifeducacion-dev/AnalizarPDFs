from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import re
import tempfile
import os

app = Flask(__name__)

# 🔥 CORS TOTAL (modo seguro para debugging)
CORS(app, supports_credentials=False)

regex_dni = re.compile(r"\*{4}\d{3,4}\*")
VALORES_ADMITIDO = {"04"}

@app.route("/analizar", methods=["POST", "OPTIONS"])
def analizar():

    # 🔥 responder preflight SIEMPRE
    if request.method == "OPTIONS":
        return "", 204

    try:
        if "pdf" not in request.files:
            return jsonify({"error": "No PDF"}), 400

        pdf_file = request.files["pdf"]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            pdf_file.save(temp.name)
            path = temp.name

        resultados = {
            "Especialidad": {
                "total": 0,
                "admitidos": 0
            }
        }

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

        # 🔥 respuesta OK
        return jsonify(resultados), 200

    except Exception as e:
        # 🔥 MUY IMPORTANTE: CORS también en errores
        response = jsonify({"error": str(e)})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500


if __name__ == "__main__":
    app.run()
