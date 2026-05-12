from app.extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=True)

    google_id = db.Column(db.String(150), nullable=True, unique=True)
    auth_provider = db.Column(db.String(20), default="email")
    role = db.Column(db.String(20), default="user")      # user / admin
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255), nullable=True)
    reset_password_token = db.Column(db.String(255), nullable=True)
    
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    height = db.Column(db.Integer, nullable=True)  # cm
    weight = db.Column(db.Integer, nullable=True)  # kg

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # relasi ke screening
    screenings = db.relationship(
        "Screening",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "auth_provider": self.auth_provider,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "has_password": True if self.password else False,
            "date_of_birth": self.date_of_birth,
            "gender": self.gender,
            "height": self.height,
            "weight": self.weight,
            "created_at": self.created_at
        }
    
    def to_admin_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            # "google_id": self.google_id,
            # "verification_token": self.verification_token,
            "deleted_at": self.deleted_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }