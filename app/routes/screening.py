from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.screening import Screening
from datetime import datetime
import joblib
from app.utils.recommendation import generate_health_recommendations

screening = Blueprint("screening", __name__)
model = joblib.load("model/model_hipertensi.pkl")

# HELPER BMI
def calculate_bmi(height, weight):
    return weight / ((height / 100) ** 2)

# HELPER KLASIFIKASI TEKANAN DARAH
def classify_bp(sys, dia):
    if sys < 120 and dia < 80:
        return "normal"
    elif sys < 140:
        return "prehypertension"
    else:
        return "hypertension"

# CREATE SCREENING
@screening.route("/screening", methods=["POST"])
@jwt_required()
def create_screening():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    try:
        # HITUNG BMI
        bmi = calculate_bmi(data["height"], data["weight"])

        # KLASIFIKASI BP
        bp_category = classify_bp(
            data["systolic"],
            data["diastolic"]
        )

        bp_map = {
            "normal": 0,
            "prehypertension": 1,
            "hypertension": 2
        }

        med_map = {
            "none": 0,
            "beta blocker": 1,
            "diuretic": 2,
            "ace inhibitor": 3,
            "other": 4
        }

        exercise_map = {
            "low": 0,
            "moderate": 1,
            "high": 2
        }

        yesno_map = {
            "no": 0,
            "yes": 1
        }

        required_fields = [
            "age", "gender", "height", "weight",
            "systolic", "diastolic",
            "salt_intake", "sleep_duration", "stress_level",
            "bp_history", "medication", "family_history",
            "exercise_level", "smoking_status"
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({"message": f"{field} is required"}), 400

        # PREPARE DATA KE MODEL
        features = [
            data["age"],
            data["salt_intake"],
            data["stress_level"],
            bp_map[data["bp_history"].lower()],
            data["sleep_duration"],
            bmi,
            med_map[data["medication"].lower()],
            yesno_map[data["family_history"].lower()],
            exercise_map[data["exercise_level"].lower()],
            yesno_map[data["smoking_status"].lower()]
        ]

        # PREDICT AI
        prediction = model.predict([features])[0]
        smoking_bool = True if data["smoking_status"].lower() == "yes" else False  
        family_bool = True if data["family_history"].lower() == "yes" else False
        prediction_label = "Berisiko" if prediction == 1 else "Tidak Berisiko"
        recommendations = generate_health_recommendations({
            "prediction": prediction_label,
            "age": data["age"],
            "systolic": data["systolic"],
            "diastolic": data["diastolic"],
            "salt_intake": data["salt_intake"],
            "sleep_duration": data["sleep_duration"],
            "stress_level": data["stress_level"],
            "bmi": bmi,
            "smoking_status": smoking_bool,
            "family_history": family_bool,
            "exercise_level": data["exercise_level"],
            "medication": data["medication"],
            "bp_category": bp_category
        })

        # SIMPAN KE DB
        screening = Screening(
            user_id=user_id,

            age=data["age"],
            gender=data["gender"],
            height=data["height"],
            weight=data["weight"],
            bmi=bmi,

            systolic=data["systolic"],
            diastolic=data["diastolic"],
            bp_category=bp_category,

            salt_intake=data["salt_intake"],
            sleep_duration=data["sleep_duration"],
            smoking_status=smoking_bool,
            exercise_level=data["exercise_level"],
            medication=data["medication"],
            family_history=family_bool,
            stress_level=data["stress_level"],

            prediction=prediction_label,
        )

        db.session.add(screening)
        db.session.commit()
        

        return jsonify({
            "message": "Screening berhasil",
            "data": screening.to_dict(),
            "recommendations": recommendations
        }), 201

    except Exception as e:
        return jsonify({
            "message": "Error processing screening",
            "error": str(e)
        }), 500

# GET HISTORY
@screening.route("/screening/history", methods=["GET"])
@jwt_required()
def get_history():
    user_id = int(get_jwt_identity())

    screenings = Screening.query.filter_by(user_id=user_id)\
        .order_by(Screening.created_at.desc())\
        .all()

    return jsonify([s.to_dict() for s in screenings]), 200

# GET DETAIL
@screening.route("/screening/<int:id>", methods=["GET"])
@jwt_required()
def get_detail(id):
    user_id = int(get_jwt_identity())

    screening = Screening.query.filter_by(
        id=id,
        user_id=user_id
    ).first()

    if not screening:
        return jsonify({"message": "Data not found"}), 404

    screening_data = screening.to_dict()
    recommendations = generate_health_recommendations(screening_data)

    return jsonify({
        **screening_data,
        "recommendations": recommendations
    }), 200