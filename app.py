import os
from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import mysql.connector
from werkzeug.utils import secure_filename

app = Flask(__name__)


UPLOAD_FOLDER = 'uploads/documentos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Conexión a MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="optiadmin"
)

#Diseño de la credencial
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class CredencialPDF(FPDF):
    def design(self, nombre, puesto, vigen,cuatri,carrera, foto_path, qr_path):
        self.add_page()
        
        # Dibujar un borde/fondo de tarjeta (ID-1 size aprox: 85x54mm)
        self.set_fill_color(133, 133, 133)
        self.rect(10, 10, 
                  85, 54, 'DF')

        # Dibujar un borde/fondo de tarjeta (ID-1 size aprox: 85x54mm)
        self.set_fill_color(133, 133, 133)
        self.rect(10, 70, 
                  85, 54, 'DF')
        
        self.set_fill_color(0, 0, 0)
        self.rect(45, 110, 
                  45, 1, 'DF')
        
        # Encabezado azul
        self.set_fill_color(112, 255, 241)
        self.rect(10, 10, 85, 10, 'F')
        
        self.set_text_color(0, 0, 0)
        self.set_font("Arial", 'B', 12)
        self.text(15, 17, "CREDENCIAL CORPORATIVA")
        
        # Insertar Foto
        if foto_path:
            self.image(foto_path, x=15, y=25, w=25, h=25)

        if qr_path:
            self.image(qr_path, x=15, y=85, w=25, h=25)
        
        # Datos del empleado
        self.set_text_color(0, 0, 0)
        self.set_font("Arial", 'B', 11)
        self.text(45, 35, f"Nombre: {nombre}")
        
        self.set_font("Arial", '', 10)
        self.text(45, 42, f"Puesto: {puesto}")
        
        self.set_font("Arial", '', 10)
        self.text(45, 49, f"vigencia: {vigen}")
        
        self.set_font("Arial", '', 10)
        self.text(45, 90, f"Area: {carrera}")

        self.set_font("Arial", '', 10)
        self.text(45, 100, "Firma")

#Diseño del pdf de conta
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'RECIBO DE NÓMINA', 0, 1, 'C')
        self.ln(10)

@app.route('/')
def index():
    return render_template('index.html')



#enlaces
@app.route('/crede')
def crede():
    return render_template ("crede.html")

@app.route('/form')
def form():
    return render_template("formu.html")

@app.route('/conta')
def conta():
    return render_template("conta.html")


@app.route('/examen')
def examen():
    return render_template("examen.html")

#crdencial
@app.route('/generar', methods=['POST'])
def generar():
    nombre = request.form.get('nombre')
    puesto = request.form.get('puesto')
    vigen = request.form.get('vigen')
    cuatri = request.form.get('cuatri')
    carrera = request.form.get('carrera')
    qr = request.files['qr']
    foto = request.files['foto']
    
    foto_path = os.path.join(UPLOAD_FOLDER, foto.filename)
    foto.save(foto_path)
    
    qr_path = os.path.join(UPLOAD_FOLDER, qr.filename)
    qr.save(qr_path)
    
    pdf = CredencialPDF(orientation='P', unit='mm', format='A4')
    pdf.design(nombre, puesto,vigen,cuatri,carrera,  foto_path, qr_path)
    
    output_path = "uploads/credenciales/credencial.pdf"
    pdf.output(output_path)
    
    return send_file(output_path, as_attachment=True)

#conta
@app.route('/calcular', methods=['POST'])
def calcular():
    # Obtención de datos del formulario
    nombre = request.form['nombre']
    sueldo_diario = float(request.form['sueldo_diario'])
    dias_trabajados = int(request.form['dias_trabajados'])
    faltas = int(request.form['faltas'])
    percepciones_extra = float(request.form['percepciones'])
    deducciones_extra = float(request.form['deducciones'])

    # Cálculos
    monto_faltas = faltas * sueldo_diario
    subtotal = sueldo_diario * dias_trabajados
    total_pagar = (subtotal + percepciones_extra) - (monto_faltas + deducciones_extra)

    # Generación de PDF
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    datos = [
        f"Nombre del Empleado: {nombre}",
        f"Sueldo Diario: ${sueldo_diario:.2f}",
        f"Días Trabajados: {dias_trabajados}",
        f"Faltas: {faltas}",
        f"Descuento por Faltas: ${monto_faltas:.2f}",
        f"Otras Percepciones: ${percepciones_extra:.2f}",
        f"Otras Deducciones: ${deducciones_extra:.2f}",
        f"---------------------------------------",
        f"TOTAL A PAGAR: ${total_pagar:.2f}"
    ]

    for linea in datos:
        pdf.cell(200, 10, txt=linea, ln=True)

    pdf_file = "uploads/recibos/recibo_nomina.pdf"
    pdf.output(pdf_file)

    return send_file(pdf_file, as_attachment=True)

#examen
@app.route('/resultado', methods=['POST'])
def resultado():
    puntos = 0

    # Sumamos puntos de las 8 preguntas
    for i in range(1, 9):
        respuesta = request.form.get(f"p{i}")
        if respuesta:
            puntos += int(respuesta)

    # Evaluación final
    if puntos >= 22:
        mensaje = "Perfil Excelente 🏆"
    elif puntos >= 18:
        mensaje = "Perfil Bueno ✅"
    elif puntos >= 14:
        mensaje = "Perfil Regular ⚠️"
    else:
        mensaje = "Perfil Bajo ❌"

    return render_template("resultado.html", puntos=puntos, mensaje=mensaje)

# registro formulario
@app.route('/registrar', methods=['POST'])
def registrar():
    nombre = request.form['nombre']
    apellido_p = request.form['apellido_p']
    apellido_m = request.form['apellido_m']
    email = request.form['correo']
    tel = request.form['numero']
    pdf = request.files['documento']

    cursor = db.cursor()

    # 1️⃣ Insertar datos sin archivo primero
    sql = 'INSERT INTO registro_as(nombre, apellido_p, apellido_m, correo, numero_t, cv_url) VALUES (%s,%s,%s,%s,%s,%s)'
    values = (nombre, apellido_p, apellido_m, email, tel, "")  # temporalmente vacío
    cursor.execute(sql, values)
    db.commit()

    # 2️⃣ Obtener el ID generado automáticamente
    user_id = cursor.lastrowid  # Esto corresponde a id_as

    # 3️⃣ Crear carpeta específica para este ID
    carpeta_usuario = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
    os.makedirs(carpeta_usuario, exist_ok=True)

    # 4️⃣ Guardar el archivo dentro de la carpeta del usuario
    if pdf:
        nombre_seguro = secure_filename(pdf.filename)
        ruta_guardado = os.path.join(carpeta_usuario, nombre_seguro)
        pdf.save(ruta_guardado)

        # 5️⃣ Guardar la URL relativa en la base de datos
        url_archivo = f"documentos/{user_id}/{nombre_seguro}"
        sql_update = 'UPDATE registro_as SET cv_url=%s WHERE id_as=%s'
        cursor.execute(sql_update, (url_archivo, user_id))
        db.commit()
    return render_template("index.html", mensaje="Usuario registrado y archivo guardado!")

if __name__ == '__main__':
    app.run(debug=True)