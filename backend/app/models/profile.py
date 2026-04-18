from __future__ import annotations

from datetime import datetime

from app.extensions import db


class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    full_name = db.Column(db.String(200), default="", nullable=False)
    education = db.Column(db.Text, default="", nullable=False)
    experience = db.Column(db.Text, default="", nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="profile")
    skills = db.relationship(
        "Skill",
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="Skill.id",
    )


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    proficiency = db.Column(db.String(32), nullable=False)  # beginner | intermediate | advanced

    profile = db.relationship("StudentProfile", back_populates="skills")
