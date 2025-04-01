import pyodbc
from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

# Conexión a la base de datos
def get_db_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER= (localdb)\cinemas3;'
            'DATABASE=CineReservas;'
            'UID=sa;'
            'PWD=1234567;'
            'TrustServerCertificate=yes;'
        )
        return conn
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return None

# Usuarios para autenticación
usuarios = {
    "juan": "2025",
    "maria": "2025"
}

@auth.verify_password
def verify_password(usuario, contraseña):
    if usuario in usuarios and usuarios[usuario] == contraseña:
        return usuario
    return None

# Endpoint para obtener la estructura de las tablas con su nombre y valores predeterminados
@app.route('/tablas', methods=['GET'])
@auth.login_required
def get_tablas():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = conn.cursor()
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    tablas = [row[0] for row in cursor.fetchall()]
    
    resultado = {}

    for tabla in tablas:
        cursor.execute(f"SELECT TOP 1 * FROM {tabla}")  # Solo obtiene una fila de muestra
        columnas = [column[0] for column in cursor.description]  # Obtiene los nombres de las columnas

        resultado[tabla] = columnas  # Guarda la estructura bajo el nombre de la tabla

        # Obtener valores predeterminados de cada columna
        cursor.execute(f"""
            SELECT COLUMN_NAME, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{tabla}'
        """)
        
        valores_predeterminados = {row[0]: row[1] for row in cursor.fetchall()}

        # Agregar los valores predeterminados al resultado
        resultado[tabla] = {
            "columnas": columnas,
            "valores_predeterminados": valores_predeterminados
        }

    conn.close()
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(port=5050, debug=True)
