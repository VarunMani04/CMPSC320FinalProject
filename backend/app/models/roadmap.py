from __future__ import annotations

from datetime import datetime

from app.extensions import db


class Roadmap(db.Model):
    """One roadmap row per user; regenerated replaces content."""

    __tablename__ = "roadmaps"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False, index=True)
    milestones_json = db.Column(db.Text, nullable=False, default="{}")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref=db.backref("roadmap", uselist=False))
