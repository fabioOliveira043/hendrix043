from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database import get_db

shop_bp = Blueprint("shop", __name__)

@shop_bp.route("/")
def home():
    products = get_db().execute("SELECT * FROM products WHERE active=1 ORDER BY id DESC").fetchall()
    return render_template("home.html", products=products)

@shop_bp.route("/produto/<int:product_id>")
def product_detail(product_id):
    product = get_db().execute("SELECT * FROM products WHERE id=? AND active=1", (product_id,)).fetchone()
    if not product:
        return render_template("404.html"), 404
    return render_template("product.html", product=product)

@shop_bp.route("/carrinho")
def cart():
    cart_data = session.get("cart", {})
    items, total = [], 0
    db = get_db()
    for product_id, quantity in cart_data.items():
        product = db.execute("SELECT * FROM products WHERE id=? AND active=1", (int(product_id),)).fetchone()
        if product:
            qty = max(1, min(int(quantity), 99))
            subtotal = product["price_cents"] * qty
            items.append({"product": product, "quantity": qty, "subtotal": subtotal})
            total += subtotal
    return render_template("cart.html", items=items, total=total)

@shop_bp.route("/carrinho/adicionar/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = get_db().execute("SELECT id FROM products WHERE id=? AND active=1", (product_id,)).fetchone()
    if not product:
        flash("Produto não encontrado.", "error")
        return redirect(url_for("shop.home"))
    cart = session.get("cart", {})
    qty = int(request.form.get("quantity", 1))
    qty = max(1, min(qty, 99))
    cart[str(product_id)] = min(int(cart.get(str(product_id), 0)) + qty, 99)
    session["cart"] = cart
    flash("Produto adicionado ao carrinho.", "success")
    return redirect(url_for("shop.cart"))

@shop_bp.route("/carrinho/atualizar", methods=["POST"])
def update_cart():
    cart = session.get("cart", {})
    for key in list(cart.keys()):
        try:
            qty = int(request.form.get(f"qty_{key}", 0))
        except ValueError:
            qty = 0
        if qty <= 0:
            cart.pop(key, None)
        else:
            cart[key] = min(qty, 99)
    session["cart"] = cart
    flash("Carrinho atualizado.", "success")
    return redirect(url_for("shop.cart"))

@shop_bp.route("/finalizar-pedido", methods=["POST"])
def checkout():
    if not session.get("user_id"):
        flash("Entre na sua conta para finalizar o pedido.", "error")
        return redirect(url_for("auth.login"))
    cart = session.get("cart", {})
    if not cart:
        flash("Seu carrinho está vazio.", "error")
        return redirect(url_for("shop.cart"))
    db = get_db()
    valid_items, total = [], 0
    for pid, qty in cart.items():
        product = db.execute("SELECT * FROM products WHERE id=? AND active=1", (int(pid),)).fetchone()
        if product:
            qty = max(1, min(int(qty), 99))
            valid_items.append((product, qty))
            total += product["price_cents"] * qty
    if not valid_items:
        flash("Não há produtos válidos no carrinho.", "error")
        return redirect(url_for("shop.cart"))
    cur = db.execute("INSERT INTO orders(user_id,total_cents,status,payment_status) VALUES(?,?,?,?)",
                     (session["user_id"], total, "Recebido", "Pendente"))
    order_id = cur.lastrowid
    for product, qty in valid_items:
        db.execute("""INSERT INTO order_items(order_id,product_id,product_name,quantity,unit_price_cents)
                      VALUES(?,?,?,?,?)""",
                   (order_id, product["id"], product["name"], qty, product["price_cents"]))
    db.commit()
    session["cart"] = {}
    flash(f"Pedido #{order_id} registrado! Pagamento pendente de confirmação.", "success")
    return redirect(url_for("shop.my_orders"))

@shop_bp.route("/meus-pedidos")
def my_orders():
    if not session.get("user_id"):
        flash("Faça login para consultar seus pedidos.", "error")
        return redirect(url_for("auth.login"))
    orders = get_db().execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC",
                              (session["user_id"],)).fetchall()
    return render_template("orders.html", orders=orders)
