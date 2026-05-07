from flask import Flask, request, jsonify
import pdfplumber
import re
import tempfile
import os

app = Flask(__name__)

regex_dni = re.compile(r"\*{4}\d{3,4}\*")
VALORES_ADMITIDO = {"04"}

@app.route("/", methods=["POST"])
def analizar():

    if "pdf" not in request.files:
        return jsonify({"error": "No se envió PDF"})

    pdf_file = request.files["pdf"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        pdf_file.save(temp.name)
        pdf_path = temp.name

    resultados = {
        "Especialidad": {
            "total": 0,
            "admitidos": 0
        }
    }

    try:

        with pdfplumber.open(pdf_path) as pdf:

            for pagina in pdf.pages:

                words = pagina.extract_words()

                filas = {}

                for w in words:
                    y = round(w["top"], 0)
                    filas.setdefault(y, []).append(w)

                for fila in filas.values():

                    texto_fila = [w["text"] for w in fila]

                    dnis = [t for t in texto_fila if regex_dni.match(t)]

                    if not dnis:
                        continue

                    resultados["Especialidad"]["total"] += len(dnis)

                    tipos = [t for t in texto_fila if t in VALORES_ADMITIDO]

                    resultados["Especialidad"]["admitidos"] += len(tipos)

        return jsonify(resultados)

    finally:
        os.remove(pdf_path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
