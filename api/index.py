import fitz
import io
from flask import Flask, request, send_file, render_template

app = Flask(__name__, template_folder="../templates")

# Coordenada Y calibrada para que baje al renglón correcto (antes salía muy arriba)
COORD_X = 326 
COORD_Y = 163 

@app.route("/procesar", methods=["POST"])
def procesar():
    try:
        lugar = request.form.get("lugar", "CUAUHTÉMOC, CDMX").upper()
        fecha_raw = request.form.get("fecha")
        archivo = request.files.get("archivo_pdf")

        if not archivo or not fecha_raw:
            return "Faltan datos", 400

        # Formateo manual para evitar fallos de librería datetime
        y, m, d = fecha_raw.split('-')
        meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", 
                 "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        texto_final = f"{lugar} A {int(d)} DE {meses[int(m)-1]} DE {y}"

        # Leer PDF desde el buffer de memoria
        stream = archivo.read()
        with fitz.open(stream=stream, filetype="pdf") as doc:
            page = doc[0]

            # [span_3](start_span)Parche blanco: cubrimos el área de "Lugar y Fecha de Emisión"[span_3](end_span)
            # [span_4](start_span)Ensanchamos para borrar completamente el texto previo[span_4](end_span)
            rect = fitz.Rect(COORD_X - 10, COORD_Y - 12, 585, COORD_Y + 5)
            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

            # Insertamos el nuevo texto
            page.insert_text((COORD_X, COORD_Y), texto_final, fontsize=7, fontname="hebo")

            output = io.BytesIO()
            doc.save(output)
            output.seek(0)

        return send_file(output, mimetype="application/pdf", as_attachment=True, download_name="Actualizado.pdf")

    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/")
def home():
    return render_template("index.html")
    
