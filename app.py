from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from fpdf import FPDF
import os
from datetime import datetime
from io import BytesIO
import xlsxwriter  # pip install xlsxwriter

app = Flask(__name__)
app.secret_key = "dev-secret"  # para mensajes flash

# Ruta del catálogo (similar a tu CATALOGO_PATH en Colab)
 
CATALOGO_PATH = os.path.join("static", "catalogo")

# --- Datos del catálogo (mismos precios que tu Colab) ---
PRECIOS = {
    1: 15000,  2: 22000,  3: 18000,  4: 30000,  5: 25000,
    6: 17000,  7: 21000,  8: 35000,  9: 27000, 10: 40000,
    11: 19500, 12: 28900, 13: 31500, 14: 12000, 15: 23000,
    16: 19900, 17: 28000, 18: 33000, 19: 45000, 20: 50000
}

PRODUCTO = {
    1: "Crema Corporal",  2: "Shampoo",  3: "Limpiador Facial",  4: "Exfoliante",  5: "Mascarilla",
    6: "Espuma de Afeitar",  7: "Balsamo PostBarba",  8: "Oleo Barba",  9: "Cera", 10: "Desodorante",
    11: "Protector Solar", 12: "Serum", 13: "Antiseñales", 14: "Contorno de Ojos", 15: "Jabon de Baño",
    16: "Hidratante Labial", 17: "Fragancia Amaderada", 18: "Eau de Parfume Elo", 19: "Eua de Parfum Coragio", 20: "Eau de Toilette Horus"
}

PRODUCTS = [
    {"id": i, "name": PRODUCTO[i], "price": PRECIOS[i], "image": f"catalogo/({i}).jpeg"}
    for i in range(1, 21)
]

# ----------------- helpers carrito -----------------
def _cart():
    if "cart" not in session:
        session["cart"] = {}
    return session["cart"]

def _cart_count():
    c = _cart()
    return sum(c.values()) if c else 0

# --- MENÚ PRINCIPAL (Inicio) ---
@app.route("/")
def home():
    return render_template("index.html", cart_count=_cart_count())

# --- SOBRE NOSOTROS ---
@app.route("/about")
def about():
    # Links que usaste en Colab
    link_word = "https://docs.google.com/document/d/1TuZWbwD3CI-J5NRNt1xsmDwDykqynNcaxprjtP55oh0/edit?usp=sharing"
    link_ppt  = "https://docs.google.com/presentation/d/1jVTFjlSIlCM7GrNxhs0M6ptI6PUIEDEa/edit?usp=sharing&ouid=117299082423511242657&rtpof=true&sd=true"
    return render_template("about.html", link_word=link_word, link_ppt=link_ppt, cart_count=_cart_count())

# --- CATÁLOGO: PDF (tu ruta original, intacta) ---
@app.route("/catalogo/generar")
def catalogo_generar():
    # Crear PDF
    pdf = FPDF("P", "mm", "A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Catalogo de Productos", ln=True, align="C")
    pdf.ln(3)

    # Layout
    x = 15; y = 30; paso_x = 45; paso_y = 49; w = 38; h = 38
    n = 1
    for fila in range(5):
        for col in range(4):
            ruta = os.path.join(CATALOGO_PATH, f"({n}).jpeg")
            x_img = x + col * paso_x + (paso_x - w) / 2
            y_img = y + fila * paso_y

            if os.path.exists(ruta):
                pdf.image(ruta, x=x_img, y=y_img, w=w, h=h)
            else:
                pdf.set_xy(x_img, y_img + h/2)
                pdf.set_font("Arial", size=8)
                pdf.cell(w=40, h=5, txt=f"Falta ({n}).jpeg", border=0, align="C")

            pdf.set_xy(x + col * paso_x, y_img + h + 2)
            pdf.set_font("Arial", size=8)
            precio = PRECIOS.get(n, "N/A")
            nombre_producto = PRODUCTO.get(n, "N/A")
            pdf.cell(w=paso_x, h=5, txt=f"{nombre_producto} - ${precio}", border=0, align="C")

            n += 1
            if n > 20:
                break
        if n > 20:
            break

    # Guardar con timestamp
    filename = f"CatalogoProductos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    out_path = os.path.join("static", filename)
    pdf.output(out_path)

    flash("✅ Catálogo PDF generado correctamente.")
    return send_file(out_path, as_attachment=True)

# --- VISTA del catálogo (grid con precios y botón carrito) ---
@app.route("/catalogo")
def catalogo():
    return render_template("catalogo.html", products=PRODUCTS, cart_count=_cart_count())

# Añadir al carrito (sencillo, solo contador por id)
@app.post("/cart/add/<int:pid>")
def add_to_cart(pid):
    cart = _cart()
    pid = str(pid)
    cart[pid] = cart.get(pid, 0) + 1
    session.modified = True
    flash("🛒 Producto añadido al carrito.")
    return redirect(url_for("catalogo"))

# --- Exportar a Excel (sin pandas, usando xlsxwriter) ---
@app.route("/catalogo/export_excel")
def catalogo_export_excel():
    out = BytesIO()
    wb = xlsxwriter.Workbook(out, {'in_memory': True})
    ws = wb.add_worksheet("Catalogo")

    # Formatos
    head = wb.add_format({'bold': True, 'bg_color': '#EAF8E3', 'border': 1})
    money = wb.add_format({'num_format': '$ #,##0', 'border': 1})
    cell = wb.add_format({'border': 1})

    # Encabezados
    ws.write_row(0, 0, ["ID", "Nombre", "Precio"], head)

    # Filas
    for i, p in enumerate(PRODUCTS, start=1):
        ws.write_number(i, 0, p["id"], cell)
        ws.write(i, 1, p["name"], cell)
        ws.write_number(i, 2, p["price"], money)

    # Anchos
    ws.set_column("A:A", 6)
    ws.set_column("B:B", 28)
    ws.set_column("C:C", 14)

    wb.close()
    out.seek(0)
    return send_file(
        out,
        as_attachment=True,
        download_name="catalogo.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- CHAT simple (cliente) ---
@app.route("/chat")
def chat():
    return render_template("chat.html", cart_count=_cart_count())

@app.route("/cart/reset")
def cart_reset():
    session.pop("cart", None)
    session.modified = True
    flash("🧹 Carrito vaciado.")
    return redirect(url_for("catalogo"))


# API mínima para respuestas (compatibilidad con chat.html)
@app.route("/api/chat", methods=["POST"])
def api_chat():
    msg = (request.json.get("mensaje") or "").lower()
    if "bien" in msg :
        return {"respuesta": "Me alegro de verdad, yo muy bien gracias!, en que te puedo apoyar?"}
    if "hola" in msg:
        return {"respuesta": "¡Hola! ¿Cómo estás?"}
    if "precio" in msg:
        return {"respuesta": "Los precios están en el catálogo."}
    if "contacto" in msg or "telefono" in msg:
        return {"respuesta": "Puedes escribirnos en la sección 'Contáctenos'."}
    if "gracias" in msg:
        return {"respuesta": "¡Con mucho gusto! 😊"}
    return {"respuesta": "Lo siento, no entendí tu mensaje."}

# --- CONTÁCTENOS (formulario POST) ---
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip()
        mensaje = request.form.get("mensaje", "").strip()

        if not nombre or not correo or not mensaje:
            flash("⚠️ Por favor completa todos los campos.")
            return redirect(url_for("contact"))

        # Aquí podrías guardar en BD, enviar correo, etc.
        flash(f"✅ Gracias, {nombre}. Tu mensaje fue recibido correctamente.")
        return redirect(url_for("contact"))

    return render_template("contact.html", cart_count=_cart_count())

@app.route("/modelo-ml")
def modelo_ml():
    # vista placeholder; luego la llenamos
    return render_template("modelo_ml.html", cart_count=_cart_count())

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
