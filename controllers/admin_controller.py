from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from models.database import get_db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            abort(403)
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route("/")
@admin_required
def dashboard():
    db = get_db()
    products = db.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    orders = db.execute("""SELECT orders.*, users.name AS customer FROM orders
                           JOIN users ON users.id=orders.user_id ORDER BY orders.id DESC""").fetchall()
    return render_template("admin.html", products=products, orders=orders)

@admin_bp.route("/produto/salvar", methods=["POST"])
@admin_required
def save_product():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    try:
        price = round(float(request.form.get("price", "0")) * 100)
    except ValueError:
        price = -1
    if not name or price < 0:
        flash("Informe nome e preço válido.", "error")
        return redirect(url_for("admin.dashboard"))
    db = get_db()
    product_id = request.form.get("product_id")
    if product_id:
        db.execute("UPDATE products SET name=?,description=?,price_cents=? WHERE id=?",
                   (name, description, price, product_id))
    else:
        db.execute("INSERT INTO products(name,description,price_cents) VALUES(?,?,?)",
                   (name, description, price))
    db.commit()
    flash("Produto salvo.", "success")
    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/produto/<int:product_id>/alternar", methods=["POST"])
@admin_required
def toggle_product(product_id):
    db = get_db()
    db.execute("UPDATE products SET active=CASE active WHEN 1 THEN 0 ELSE 1 END WHERE id=?", (product_id,))
    db.commit()
    flash("Status do produto atualizado.", "success")
    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/pedido/<int:order_id>/status", methods=["POST"])
@admin_required
def update_order(order_id):
    status = request.form.get("status")
    allowed = {"Recebido", "Em preparo", "Enviado", "Concluído", "Cancelado"}
    if status not in allowed:
        flash("Status inválido.", "error")
    else:
        db = get_db()
        db.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
        db.commit()
        flash("Pedido atualizado.", "success")
    return redirect(url_for("admin.dashboard"))
