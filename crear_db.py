import sqlite3

conn = sqlite3.connect("productos.db")
cursor = conn.cursor()

# Tabla productos (contiene un campo nom_mat para el nombre del/los materiales)
cursor.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    precio REAL NOT NULL DEFAULT 0,
    tiempo REAL NOT NULL DEFAULT 0,
    tipo TEXT NOT NULL DEFAULT '',
    gramos REAL DEFAULT 0,
    materiales_unidad REAL DEFAULT 1,
    nom_mat TEXT DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# Limpiar datos previos (opcional)
cursor.execute("DELETE FROM productos")
conn.commit()

# Insertar producto de ejemplo (opcional)
cursor.execute("""
INSERT INTO productos (nombre, precio, tiempo, tipo, gramos, materiales_unidad, nom_mat)
VALUES ('Bufanda Lana', 50, 2.5, 'Lana', 200, 1, 'Ovillo lana blanco')
""")

conn.commit()
conn.close()
print("Base de datos creada con producto de ejemplo (productos.db).")
