import os, sqlite3
from flask import current_app, g
from werkzeug.security import generate_password_hash

def get_db():
    if "db" not in g:
        db_path = current_app.config["DATABASE"]
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        db_path = app.config["DATABASE"]
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        db = sqlite3.connect(db_path)
        db.execute("PRAGMA foreign_keys = ON")
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'customer',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
            image_url TEXT NOT NULL DEFAULT '',
            active INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_cents INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Recebido',
            payment_status TEXT NOT NULL DEFAULT 'Pendente',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price_cents INTEGER NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        );
        """)
        admin = db.execute("SELECT id FROM users WHERE email=?", ("admin@cafeteria.local",)).fetchone()
        if not admin:
            db.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)",
                       ("Administrador", "admin@cafeteria.local",
                        generate_password_hash("Admin123!"), "admin"))
        count = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            seed = [
                ("Café Especial Mogiana 250g", "Café em grãos com notas de chocolate e castanhas.", 3890, ""),
                ("Cappuccino da Casa", "Cappuccino cremoso preparado na hora.", 1490, ""),
                ("Cold Brew 300ml", "Café extraído a frio, suave e refrescante.", 1690, ""),
                ("Cookie de Chocolate", "Cookie artesanal com gotas de chocolate.", 990, ""),
                ("Kit Degustação", "Seleção de cafés especiais para presentear.", 7990, ""),
                ("Espresso Duplo", "Dose dupla de espresso com crema intensa.", 1200, "")
            ]
            db.executemany("INSERT INTO products(name,description,price_cents,image_url) VALUES(?,?,?,?)", seed)
        db.commit()
        db.close()
        app.teardown_appcontext(close_db)
