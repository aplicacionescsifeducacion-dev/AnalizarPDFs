from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import re
import tempfile
import os

# 🔥 PRIMERO crear app
app = Flask(__name__)

# 🔥 luego CORS
CORS(app)

regex_dni = re.compile(r"\*{4}\d{3,4}\*")
VALORES_ADMITIDO = {"04"}

@app.route("/analizar", methods=["POST", "OPTIONS"])
def analizar():

    if request.method == "OPTIONS":
        return "", 200

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run()
