from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import get_db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/cadastro", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Preencha todos os campos. A senha deve ter pelo menos 8 caracteres.", "error")
            return render_template("register.html")
        db = get_db()
        try:
            db.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
                       (name, email, generate_password_hash(password)))
            db.commit()
            flash("Cadastro realizado. Entre com seu e-mail e senha.", "success")
            return redirect(url_for("auth.login"))
        except Exception:
            flash("Não foi possível cadastrar. Verifique se o e-mail já está em uso.", "error")
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["role"] = user["role"]
            flash("Login realizado com sucesso.", "success")
            return redirect(url_for("admin.dashboard" if user["role"] == "admin" else "shop.home"))
        flash("E-mail ou senha inválidos.", "error")
    return render_template("login.html")

@auth_bp.route("/sair")
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "success")
    return redirect(url_for("shop.home"))
