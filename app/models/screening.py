from app.extensions import db
from datetime import datetime

class Screening(db.Model):
    __tablename__ = "screenings"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Personal Info Snapshot
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    bmi = db.Column(db.Float)

    # Blood Pressure
    systolic = db.Column(db.Integer)
    diastolic = db.Column(db.Integer)
    bp_category = db.Column(db.String(30))

    # Lifestyle & Health
    salt_intake = db.Column(db.Float)
    sleep_duration = db.Column(db.Float)
    smoking_status = db.Column(db.Boolean)
    exercise_level = db.Column(db.String(10))
    medication = db.Column(db.String(50))
    family_history = db.Column(db.Boolean)
    stress_level = db.Column(db.Integer)

    # AI Result
    prediction = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,

            "age": self.age,
            "gender": self.gender,
            "height": self.height,
            "weight": self.weight,
            "bmi": self.bmi,

            "systolic": self.systolic,
            "diastolic": self.diastolic,
            "bp_category": self.bp_category,

            "salt_intake": self.salt_intake,
            "sleep_duration": self.sleep_duration,
            "smoking_status": self.smoking_status,
            "exercise_level": self.exercise_level,
            "medication": self.medication,
            "family_history": self.family_history,
            "stress_level": self.stress_level,

            "prediction": self.prediction,

            "created_at": self.created_at
        }