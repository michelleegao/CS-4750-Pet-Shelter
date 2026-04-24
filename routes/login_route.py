from flask import Blueprint, render_template, request, jsonify
from db.connection import getconn
import hashlib
import uuid
from datetime import datetime

login_bp = Blueprint('login', __name__)

@login_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("create.html")

    data = request.get_json(silent=True)
    if not data:
        data = request.form

    userID = uuid.uuid4().bytes
    email = data.get("email")
    password = data.get("password")
    firstName = data.get("firstName")
    lastName = data.get("lastName")
    phoneNumber = data.get("phoneNumber")
    positionName = data.get("positionName")
    creationDateTime = datetime.utcnow()

    if not email or not password:
        return jsonify({"success": False, "message": "Missing fields"})

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = getconn()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing = cursor.fetchone()

    if existing:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "Email already exists"})

    cursor.execute(
        """INSERT INTO users 
        (userID, email, password_hash, first_name, last_name, phone_number, role, creation_date) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (userID, email, hashed_password, firstName, lastName, phoneNumber, positionName, creationDateTime)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"success": True, "message": "Account created"})


@login_bp.route("/forgot")
def forgot_page():
    return render_template("forgot.html")


@login_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Missing fields"})

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = getconn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password_hash FROM users WHERE email = %s",
        (email,)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and user[0] == hashed_password:
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid login"})


@login_bp.route("/check_user", methods=["POST"])
def check_user():
    data = request.get_json()
    email = data.get("email")

    conn = getconn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT userId FROM users WHERE email = %s",
        (email,)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify({"exists": user is not None})


@login_bp.route("/reset_password", methods=["POST"])
def reset_password():
    data = request.get_json()

    email = data.get("email")
    new_password = data.get("newPassword")

    if not email or not new_password:
        return jsonify({"success": False, "message": "Missing fields"})

    hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

    conn = getconn()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET password_hash = %s WHERE email = %s",
        (hashed_password, email)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"success": True, "message": "Password updated"})