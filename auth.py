from functools import wraps
from flask import Blueprint, request, jsonify, session
from flask_bcrypt import Bcrypt
from models import db, User, Ledger

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Login required"}), 401
        return fn(*args, **kwargs)
    return wrapper

@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    password = str(data.get("password", ""))

    if not name or not phone or len(password) < 6:
        return jsonify({"error": "Name, phone and a password of at least 6 characters are required"}), 400

    if User.query.filter_by(phone=phone).first():
        return jsonify({"error": "Phone number already registered"}), 409

    referral_code = "UGX" + str(abs(hash(phone)))[:8]
    while User.query.filter_by(referral_code=referral_code).first():
        referral_code += "X"

    user = User(
        name=name,
        phone=phone,
        password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
        referral_code=referral_code,
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Account created",
        "referral_code": referral_code
    }), 201

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    phone = str(data.get("phone", "")).strip()
    password = str(data.get("password", ""))
    user = User.query.filter_by(phone=phone).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid phone number or password"}), 401

    session["user_id"] = user.id
    return jsonify({"message": "Logged in", "name": user.name})

@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

@auth_bp.get("/me")
@login_required
def me():
    user = db.session.get(User, session["user_id"])
    return jsonify({
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "referral_code": user.referral_code
    })
