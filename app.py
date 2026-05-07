from flask import Flask, request, jsonify
import pdfplumber
from flask_cors import CORS
import io

app = Flask(__name__)
CORS(app, resources={r"/*": {
    "origins": "*",
    "allow_headers": ["Content-Type", "API-KEY"],
    "methods": ["GET", "POST", "OPTIONS"]
}})

@app.route('/')
def index():
    return jsonify({"status": "API funcionando"})

@app.route('/analizar', methods=['POST'])
def analizar():
    try:
        # 🔐 API KEY
        if request.headers.get("API-KEY") != "12345":
            return jsonify({"error": "No autorizado"}), 403

        # 📄 PDF
        if 'pdf' not in request.files:
            return jsonify({"error": "No PDF recibido"}), 400

        archivo = request.files['pdf']
        pdf_bytes = archivo.read()

        total_lineas_con_04 = 0

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:

            for pagina in pdf.pages:
                words = pagina.extract_words()

                # Agrupar por líneas (eje Y)
                filas = {}
                for w in words:
                    y = round(w["top"], 0)
                    filas.setdefault(y, []).append(w)

                # Procesar líneas
                for fila in filas.values():

                    # 🔥 clave: comparar palabra exacta
                    if any(w["text"].strip() == "04" for w in fila):
                        total_lineas_con_04 += 1

        return jsonify({
            "lineas_con_04": total_lineas_con_04
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500


if __name__ == '__main__':
    app.run(debug=True)
