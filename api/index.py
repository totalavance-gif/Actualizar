import fitz
import io
import os
from flask import Flask, request, send_file, render_template

app = Flask(__name__, template_folder="../templates")

# Coordenadas calibradas para el renglón de fecha
COORD_X = 326  # 318 + offset
COORD_Y = 163  # Calibración exacta para el renglón superior

@app.route("/procesar", methods=["POST"])
def procesar():
    doc = None
    try:
        lugar = request.form.get("lugar", "CUAUHTÉMOC, CDMX").upper()
        fecha_raw = request.form.get("fecha")
        archivo = request.files.get("archivo_pdf")

        if not archivo or not fecha_raw:
            return "Faltan datos o archivo", 400

        # Formateo manual de fecha
        y, m, d = fecha_raw.split('-')
        meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", 
                 "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        texto_final = f"{lugar} A {int(d)} DE {meses[int(m)-1]} DE {y}"

        # Procesamiento
        pdf_bytes = archivo.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]

        # PARCHE: Borrar texto anterior
        # Ensanchamos el rectángulo para asegurar que borre "TLALMANALCO..."
        rect_blanco = fitz.Rect(COORD_X - 10, COORD_Y - 12, 585, COORD_Y + 5)
        page.draw_rect(rect_blanco, color=(1, 1, 1), fill=(1, 1, 1))

        # ESCRIBIR
        page.insert_text((COORD_X, COORD_Y), texto_final, fontsize=7, fontname="hebo")

        output = io.BytesIO()
        doc.save(output)
        output.seek(0)

        return send_file(
            output,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"CSF_ACTUALIZADA.pdf"
        )

    except Exception as e:
        return f"Error interno: {str(e)}", 500
    finally:
        if doc: doc.close()

@app.route("/")
def home():
    return render_template("index.html")
    
