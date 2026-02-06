import fitz
import io
import os
from flask import Flask, request, send_file, render_template

app = Flask(__name__, template_folder="../templates")

# --- AJUSTE DE COORDENADAS ---
# Bajamos el valor de COORD_Y para que el texto descienda a la posición correcta
COORD_X = 318 
COORD_Y = 163  # Antes estaba en 150, lo bajamos a 163 para alinear con el original

@app.route("/procesar", methods=["POST"])
def procesar():
    doc = None
    try:
        lugar = request.form.get("lugar", "CUAUHTÉMOC, CDMX").upper()
        fecha_raw = request.form.get("fecha")
        archivo = request.files.get("archivo_pdf")

        if not archivo or not fecha_raw:
            return "Datos incompletos", 400

        # [span_1](start_span)Formateo de fecha estilo SAT[span_1](end_span)
        y_c, m_c, d_c = fecha_raw.split('-')
        meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", 
                 "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        fecha_texto = f"{int(d_c)} DE {meses[int(m_c)-1]} DE {y_c}"
        texto_final = f"{lugar} A {fecha_texto}"

        pdf_bytes = archivo.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]

        # 1. [span_2](start_span)PARCHE BLANCO: Ahora con la nueva coordenada para tapar bien[span_2](end_span)
        # Rect(x0, y0, x1, y1)
        rect_blanco = fitz.Rect(COORD_X - 5, COORD_Y - 10, 585, COORD_Y + 2)
        page.draw_rect(rect_blanco, color=(1, 1, 1), fill=(1, 1, 1))

        # 2. INSERTAR TEXTO NUEVO
        page.insert_text(
            (COORD_X, COORD_Y),
            texto_final,
            fontsize=7,
            [span_3](start_span)fontname="hebo" # Helvetica-Bold para igualar el original[span_3](end_span)
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
    
