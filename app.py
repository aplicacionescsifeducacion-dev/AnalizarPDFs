@app.route("/analizar", methods=["POST", "OPTIONS"])
def analizar():

    try:

        if request.method == "OPTIONS":
            return "", 200

        if "pdf" not in request.files:
            return jsonify({"error": "No se envió PDF"}), 400

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

        os.remove(pdf_path)

        return jsonify(resultados)

    except Exception as e:
        # 🔥 ESTO TE VA A DECIR EL PROBLEMA REAL
        return jsonify({
            "error": str(e)
        }), 500
