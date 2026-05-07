import pdfplumber
import re
from collections import defaultdict
import sys
import json

PDF_PATH = sys.argv[1]

resultados = {"total": 0, "admitidos": 0}

regex_dni = re.compile(r"\*{4}\d{3,4}\*")
VALORES_ADMITIDO = {"04"}

with pdfplumber.open(PDF_PATH) as pdf:
    for pagina in pdf.pages:

        words = pagina.extract_words()

        # 🔹 Agrupar por líneas (y)
        filas = {}

        for w in words:
            y = round(w["top"], 0)
            filas.setdefault(y, []).append(w)

        # 🔹 Procesar cada fila
        for fila in filas.values():

            texto_fila = [w["text"] for w in fila]

            # Buscar DNI en la fila
            dnis = [t for t in texto_fila if regex_dni.match(t)]

            if not dnis:
                continue

            resultados["total"] += len(dnis)

            # Buscar tipo en la misma fila
            tipos = [t for t in texto_fila if t in VALORES_ADMITIDO]

            resultados["admitidos"] += len(tipos)

print(json.dumps(resultados, indent=2))