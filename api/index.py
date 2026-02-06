import fitz  # PyMuPDF
import io
import os
from datetime import datetime
from flask import Flask, request, send_file, render_template

app = Flask(__name__, template_folder="../templates")

# Configuración de coordenadas basadas en el PDF de Mariana
PAGE_H = 792
COORD_X = 310 + 8  # Ajuste con el Offset
COORD_Y_BASE = 648 # Coordenada desde abajo

def get_y(pt):
    # Convertimos de ReportLab a PyMuPDF (792 - pt - offset)
    return PAGE_H - pt - 6

@app.route("/procesar", methods=["POST"])
def procesar():
    doc = None
    try:
        # 1. Obtener datos del formulario
        lugar = request.form.get("lugar", "CUAUHTÉMOC, CDMX").upper()
        fecha_input = request.form.get("fecha") # Viene como YYYY-MM-DD
        archivo = request.files.get("archivo_pdf")

        if not archivo:
            return "No subiste ningún archivo PDF", 400

        # 2. Formatear la fecha al estilo SAT
        # Ejemplo: 2026-02-05 -> 05 DE FEBRERO DE 2026
        meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", 
                 "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        
        dt = datetime.strptime(fecha_input, "%Y-%m-%d")
        fecha_formateada = f"{dt.day} DE {meses[dt.month - 1]} DE {dt.year}"
        texto_final = f"{lugar} A {fecha_formateada}"

        # 3. Procesar el PDF en memoria
        pdf_stream = archivo.read()
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        page = doc[0]

        # 4. BORRADO: Dibujar rectángulo blanco sobre la fecha anterior
        # Definimos el área a limpiar (X_inicio, Y_inicio, X_fin, Y_fin)
        rect_limpiar = fitz.Rect(COORD_X - 5, get_y(COORD_Y_BASE) - 10, 580, get_y(COORD_Y_BASE) + 5)
        page.draw_rect(rect_limpiar, color=(1, 1, 1), fill=(1, 1, 1))

        # 5. INSERCIÓN: Escribir el nuevo lugar y fecha
        page.insert_text(
            (COORD_X, get_y(COORD_Y_BASE)),
            texto_final,
            fontsize=7,
            fontname="hebo" # Helvetica-Bold para coherencia total
        )

        # 6. Preparar descarga
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"Constancia_Actualizada.pdf"
        )

    except Exception as e:
        return f"Error en el servidor: {str(e)}", 500
    finally:
        if doc:
            doc.close()

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
      
