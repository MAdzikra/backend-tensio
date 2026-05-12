from flask import Blueprint, request, jsonify
from app.models.user import User
from app.extensions import db, bcrypt
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import timedelta
from app.utils.token_helper import generate_verification_token, verify_verification_token
from app.utils.token_helper import generate_reset_password_token, verify_reset_password_token
from app.utils.email_service import send_reset_password_email
from app.utils.email_service import send_verification_email
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from flask import current_app

auth = Blueprint("auth", __name__)

# REGISTER
@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    required_fields = ["name", "email", "password"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"message": f"{field} is required"}), 400

    if len(data["password"]) < 8:
        return jsonify({"message": "Password must be at least 8 characters"}), 400
    
    existing_user = User.query.filter_by(email=data["email"]).first()

    # JIKA EMAIL SUDAH ADA
    if existing_user:
        # akun google murni
        if existing_user.auth_provider == "google":
            return jsonify({
                "message": "This account is registered with Google. Please continue with Google."
            }), 400

        # akun sudah verified penuh
        if existing_user.is_verified:
            return jsonify({
                "message": "Email already registered"
            }), 400

        token = generate_verification_token(existing_user.email)

        # AKUN ADA TAPI BELUM VERIFIED
        existing_user.name = data["name"]
        existing_user.password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
        existing_user.auth_provider = "email"
        existing_user.verification_token = token

        db.session.commit()

        send_verification_email(existing_user.email, token)

        return jsonify({
            "message": "Account found but not verified. Verification email resent."
        }), 200
    
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    token = generate_verification_token(data["email"])

    # Buat user baru
    user = User(
        name=data["name"],
        email=data["email"],
        password=hashed_password,
        verification_token=token,
        is_verified=False,
        auth_provider="email"
    )

    db.session.add(user)
    db.session.commit()

    send_verification_email(user.email, token)

    return jsonify({
        "message": "User registered successfully. Please verify your email."
    }), 201

# VERIFY EMAIL
@auth.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):
    
    email = verify_verification_token(token)

    if not email:
        return jsonify({"message": "Invalid or expired verification link"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.is_verified:
        return jsonify({"message": "Email already verified"}), 200

    if user.verification_token != token:
        return jsonify({"message": "Verification link already expired"}), 400
    
    user.is_verified = True
    user.verification_token = None
    db.session.commit()

    return jsonify({
        "message": "Email verified successfully"
    }), 200

# LOGIN
@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    # Validasi input
    required_fields = ["email", "password"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"message": f"{field} is required"}), 400

    # Cari user
    user = User.query.filter_by(email=data["email"]).first()

    if not user:
        return jsonify({"message": "User not found"}), 404
    
    if user.deleted_at is not None:
        return jsonify({"message": "This account has been deleted"}), 403

    if not user.is_active:
        return jsonify({"message": "This account is inactive"}), 403

    if not user.is_verified:
        return jsonify({"message": "Please verify your email first"}), 403

    if user.google_id and not user.password:
        return jsonify({"message": "This account is registered with Google. Please continue with Google."}), 400

    # Cek password
    if not bcrypt.check_password_hash(user.password, data["password"]):
        return jsonify({"message": "Invalid password"}), 401

    # Generate JWT
    access_token = create_access_token(
        identity=str(user.id),
        expires_delta=timedelta(days=1)
    )

    return jsonify({
        "message": "Login successful",
        "token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email, 
            "role": user.role
        }
    }), 200

# GOOGLE AUTH
@auth.route("/google-login", methods=["POST"])
def google_login():
    data = request.get_json()
    token = data.get("token")

    if not token:
        return jsonify({"message": "Google token required"}), 400

    try:
        idinfo = id_token.verify_oauth2_token(
        token,
        grequests.Request(),
        current_app.config["GOOGLE_CLIENT_ID"]
    )

        google_id = idinfo["sub"]
        email = idinfo["email"]
        name = idinfo["name"]

    except ValueError:
        return jsonify({"message": "Invalid Google token"}), 401

    user = User.query.filter_by(email=email).first()

    if user:
        # kalau user email sama tapi belum punya google_id -> link akun
        if not user.google_id:
            user.google_id = google_id
            user.is_verified = True
            if user.auth_provider == "email":
                user.auth_provider = "both"

            db.session.commit()

    else:
        user = User(
            name=name,
            email=email,
            password="",
            google_id=google_id,
            is_verified=True,
            auth_provider="google"
        )
        db.session.add(user)
        db.session.commit()

    if user.deleted_at is not None:
        return jsonify({"message": "This account has been deleted"}), 403

    if not user.is_active:
        return jsonify({"message": "This account is inactive"}), 403

    access_token = create_access_token(
        identity=str(user.id),
        expires_delta=timedelta(days=1)
    )

    return jsonify({
        "message": "Google login successful",
        "token": access_token,
        "user": user.to_dict()
    }), 200

# SET PASSWORD
@auth.route("/set-password", methods=["POST"])
@jwt_required()
def set_password():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not new_password or not confirm_password:
        return jsonify({"message": "All password fields are required"}), 400

    if new_password != confirm_password:
        return jsonify({"message": "Password confirmation does not match"}), 400

    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    # if user.auth_provider != "google":
    if user.password:
        return jsonify({"message": "Password already exists. Use change password instead."}), 400

    user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
    if user.auth_provider == "google":
        user.auth_provider = "both"

    db.session.commit()

    return jsonify({
        "message": "Password set successfully",
        "user": user.to_dict()
    }), 200

# CHANGE PASSWORD
@auth.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    current_password = data.get("current_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not current_password or not new_password or not confirm_password:
        return jsonify({"message": "All password fields are required"}), 400

    if new_password != confirm_password:
        return jsonify({"message": "Password confirmation does not match"}), 400

    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404
    
    if not user.password:
        return jsonify({"message": "No password set yet. Use set password instead."}), 400

    if not bcrypt.check_password_hash(user.password, current_password):
        return jsonify({"message": "Current password is incorrect"}), 401

    user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")

    db.session.commit()

    return jsonify({
        "message": "Password changed successfully"
    }), 200

# FORGOT PASSWORD
@auth.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"message": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if user.google_id and not user.password:
        return jsonify({
            "message": "This account uses Google Sign-In. Please continue with Google."
        }), 400

    # demi security jangan kasih tau email ada/tidak
    if user and user.deleted_at is None and user.is_active:
        token = generate_reset_password_token(user.email)
        user.reset_password_token = token
        db.session.commit()

        send_reset_password_email(user.email, token)

    return jsonify({
        "message": "If the email is registered, reset instructions have been sent."
    }), 200

# RESET PASSWORD
@auth.route("/reset-password/<token>", methods=["PUT"])
def reset_password(token):
    data = request.get_json()

    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not new_password or not confirm_password:
        return jsonify({"message": "All password fields are required"}), 400

    if len(new_password) < 8:
        return jsonify({"message": "Password must be at least 8 characters"}), 400

    if new_password != confirm_password:
        return jsonify({"message": "Password confirmation does not match"}), 400

    email = verify_reset_password_token(token)

    if not email:
        return jsonify({"message": "Invalid or expired reset link"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.deleted_at is not None:
        return jsonify({"message": "This account has been removed"}), 403

    if user.reset_password_token != token:
        return jsonify({"message": "Reset link already used or invalid"}), 400

    user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
    user.reset_password_token = None
    user.is_verified = True

    if user.auth_provider == "google":
        user.auth_provider = "both"

    db.session.commit()

    return jsonify({
        "message": "Reset password successfully"
    }), 200