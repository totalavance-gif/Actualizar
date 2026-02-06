import fitz
import io
import os
from flask import Flask, request, send_file, render_template

app = Flask(__name__, template_folder="../templates")

# Coordenadas exactas para Lugar y Fecha
COORD_X = 318  # 310 + 8 de offset
COORD_Y = 150  # 792 - 648 + 6 (Ajustado para PyMuPDF desde arriba)

@app.route("/procesar", methods=["POST"])
def procesar():
    doc = None
    try:
        # 1. Obtener datos
        lugar = request.form.get("lugar", "CUAUHTÉMOC, CDMX").upper()
        fecha_raw = request.form.get("fecha") # YYYY-MM-DD
        archivo = request.files.get("archivo_pdf")

        if not archivo or not fecha_raw:
            return "Datos incompletos", 400

        # 2. Formatear Fecha manualmente para evitar errores de locale
        y, m, d = fecha_raw.split('-')
        meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", 
                 "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        fecha_texto = f"{int(d)} DE {meses[int(m)-1]} DE {y}"
        texto_final = f"{lugar} A {fecha_texto}"

        # 3. Procesar PDF
        pdf_bytes = archivo.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]

        # 4. PARCHE BLANCO: Cubre desde el inicio del campo hasta el final del renglón
        # Rect(x0, y0, x1, y1)
        rect_blanco = fitz.Rect(COORD_X - 5, COORD_Y - 12, 585, COORD_Y + 5)
        page.draw_rect(rect_blanco, color=(1, 1, 1), fill=(1, 1, 1))

        # 5. INSERTAR TEXTO
        page.insert_text(
            (COORD_X, COORD_Y),
            texto_final,
            fontsize=7,
            fontname="hebo" # Helvetica-Bold
        )

        output = io.BytesIO()
        doc.save(output)
        output.seek(0)

        return send_file(
            output,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="Constancia_Actualizada.pdf"
        )

    except Exception as e:
        return f"Error: {str(e)}", 500
    finally:
        if doc: doc.close()

@app.route("/")
def home():
    return render_template("index.html")
        
