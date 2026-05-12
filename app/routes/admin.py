from flask import Blueprint, request, jsonify
from sqlalchemy import func
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db, bcrypt
from app.models.user import User
from app.models.screening import Screening
from app.utils.admin_required import admin_required

admin = Blueprint("admin", __name__)

@admin.route('/dashboard-stats', methods=['GET'])
@jwt_required()
@admin_required
def admin_dashboard_stats():
    total_users = User.query.count()
    total_screenings = Screening.query.count()

    high_risk = Screening.query.filter(Screening.prediction == "Berisiko").count()
    low_risk = Screening.query.filter(Screening.prediction == "Tidak Berisiko").count()

    today = datetime.utcnow().date()
    weekly_data = []
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)

        count = Screening.query.filter(
            func.date(Screening.created_at) == day
        ).count()

        weekly_data.append({
            "day": day_names[day.weekday()],
            "screenings": count
        })

    prediction_data = [
        {"name": "Berisiko", "value": high_risk, "color": "#EF4444"},
        {"name": "Tidak Berisiko", "value": low_risk, "color": "#22C55E"}
    ]

    return jsonify({
        "totalUsers": total_users,
        "totalScreenings": total_screenings,
        "highRisk": high_risk,
        "lowRisk": low_risk,
        "predictionData": prediction_data,
        "weeklyData": weekly_data,
    })

@admin.route("/users", methods=["GET"])
@jwt_required()
@admin_required
def get_all_users():
    users = User.query.filter(User.deleted_at == None).order_by(User.created_at.desc()).all()

    return jsonify([
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "is_verified": u.is_verified,
            "created_at": u.created_at
        }
        for u in users
    ]), 200

@admin.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if "role" in data:
        user.role = data["role"]

    if "is_active" in data:
        user.is_active = data["is_active"]

    if "new_password" in data and data["new_password"]:
        hashed_password = bcrypt.generate_password_hash(data["new_password"]).decode("utf-8")
        user.password = hashed_password

        # kalau sebelumnya akun google only, sekarang jadi both karena sudah punya password
        if user.auth_provider == "google":
            user.auth_provider = "both"
    db.session.commit()

    return jsonify({"message": "User updated successfully"}), 200

@admin.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    user.deleted_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200

@admin.route("/screenings", methods=["GET"])
@jwt_required()
@admin_required
def get_all_screenings():
    screenings = Screening.query.order_by(Screening.created_at.desc()).all()

    return jsonify([
        {
            "id": s.id,
            "user_id": s.user_id,
            "user_name": s.user.name,
            "user_email": s.user.email,
            "age": s.age,
            "bmi": s.bmi,
            "gender": s.gender,
            "systolic": s.systolic,
            "diastolic": s.diastolic,
            "bp_category": s.bp_category,
            "salt_intake": s.salt_intake,
            "sleep_duration": s.sleep_duration,
            "smoking_status": s.smoking_status,
            "exercise_level": s.exercise_level,
            "family_history": s.family_history,
            "stress_level": s.stress_level,
            "prediction": s.prediction,
            "created_at": s.created_at
        }
        for s in screenings
    ]), 200

@admin.route("/screenings/<int:screening_id>", methods=["GET"])
@jwt_required()
@admin_required
def screening_detail(screening_id):
    s = Screening.query.get_or_404(screening_id)

    return jsonify({
        "id": s.id,
        "user_name": s.user.name,
        "user_email": s.user.email,
        "age": s.age,
        "gender": s.gender,
        "height": s.height,
        "weight": s.weight,
        "bmi": s.bmi,
        "systolic": s.systolic,
        "diastolic": s.diastolic,
        "bp_category": s.bp_category,
        "salt_intake": s.salt_intake,
        "sleep_duration": s.sleep_duration,
        "smoking_status": s.smoking_status,
        "exercise_level": s.exercise_level,
        "medication": s.medication,
        "family_history": s.family_history,
        "stress_level": s.stress_level,
        "prediction": s.prediction,
        "created_at": s.created_at
    }), 200