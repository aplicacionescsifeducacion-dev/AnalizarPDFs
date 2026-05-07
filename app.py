from flask import Flask, request, jsonify
import pdfplumber
import re
from collections import defaultdict
from flask_cors import CORS
import io

app = Flask(__name__)
CORS(app, resources={r"/*": {
    "origins": "*",
    "allow_headers": ["Content-Type", "API-KEY"],
    "methods": ["GET", "POST", "OPTIONS"]
}})

REGEX_ESPECIALIDAD = re.compile(r"ESPECIALIDAD\s*:\s*(.+)", re.IGNORECASE)
REGEX_SI = re.compile(r"\b04\b", re.IGNORECASE)

@app.route('/')
def index():
    return jsonify({"status": "API funcionando"})

@app.route('/analizar', methods=['POST'])
def analizar():
    try:
        # 🔐 API KEY
        if request.headers.get("API-KEY") != "12345":
            return jsonify({"error": "No autorizado"}), 403

        # 📄 PDF file
        if 'pdf' not in request.files:
            return jsonify({"error": "No PDF recibido"}), 400

        archivo = request.files['pdf']
        pdf_bytes = archivo.read()

        resultados = defaultdict(lambda: {"total": 0, "admitidos": 0})
        especialidad_actual = None

        # Abrir PDF desde memoria
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:

            for i, pagina in enumerate(pdf.pages):

                words = pagina.extract_words()

                # 🔹 Agrupar palabras por línea (eje Y)
                filas = {}
                for w in words:
                    y = round(w["top"], 0)
                    filas.setdefault(y, []).append(w)

                # 🔹 Procesar líneas ordenadas
                for y in sorted(filas.keys()):
                    fila = filas[y]
                    texto_fila = " ".join(w["text"] for w in fila).strip()

                    # DEBUG (opcional)
                    print("LINEA:", texto_fila)

                    # 🔹 Detectar especialidad
                    match = REGEX_ESPECIALIDAD.search(texto_fila)
                    if match:
                        especialidad_actual = match.group(1).strip()
                        print("Especialidad detectada:", especialidad_actual)
                        continue

                    # 🔹 Detectar "04"
                    if REGEX_SI.search(texto_fila):
                        if especialidad_actual:
                            resultados[especialidad_actual]["total"] += 1
                            resultados[especialidad_actual]["admitidos"] += 1

        return jsonify(resultados)

    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500


if __name__ == '__main__':
    app.run(debug=True)
