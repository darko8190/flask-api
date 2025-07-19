from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv
import hashlib

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
CORS(app)

# Connexion à la base de données
db_url = os.getenv("DATABASE_URL")
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

# Fonction pour hasher les mots de passe
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Route principale (pour éviter l'erreur 502 sur Render)
@app.route("/", methods=["GET"])
def home():
    return """
    <h1>🎉 API Flask en ligne</h1>
    <p>Utilise les routes <code>/register</code> et <code>/login</code> avec POST (JSON).</p>
    """

# Route d'inscription
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = hash_password(data.get("password"))

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        return jsonify({"success": False, "message": "Utilisateur déjà existant"}), 400

    cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
    conn.commit()
    return jsonify({"success": True})

# Route de connexion
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = hash_password(data.get("password"))

    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()

    if user:
        return jsonify({"success": True, "user": {"id": user[0], "name": user[1], "email": user[2]}})
    else:
        return jsonify({"success": False, "message": "Identifiants invalides"}), 401

# Lancement de l'application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
