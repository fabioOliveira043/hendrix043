from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash
from functools import wraps
from decimal import Decimal, InvalidOperation
from models.database import init_db, get_db
from controllers.auth_controller import auth_bp
from controllers.shop_controller import shop_bp
from controllers.admin_controller import admin_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = "troque-esta-chave-por-uma-chave-secreta-forte"
app.config["DATABASE"] = "database/cafeteria.db"

init_db(app)
app.register_blueprint(auth_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(admin_bp)

@app.context_processor
def inject_cart_count():
    cart = session.get("cart", {})
    return {"cart_count": sum(int(q) for q in cart.values())}

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
