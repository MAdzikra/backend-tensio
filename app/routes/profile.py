from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.extensions import db

profile = Blueprint("profile", __name__)

# GET PROFILE
@profile.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify(user.to_dict()), 200


# UPDATE PROFILE
@profile.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    # update field (opsional semua)
    user.name = data.get("name", user.name)
    user.date_of_birth = data.get("date_of_birth", user.date_of_birth)
    user.gender = data.get("gender", user.gender)
    user.height = data.get("height", user.height)
    user.weight = data.get("weight", user.weight)

    db.session.commit()

    return jsonify({
        "message": "Profile updated successfully",
        "data": user.to_dict()
    }), 200