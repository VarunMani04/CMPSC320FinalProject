from __future__ import annotations

from datetime import datetime

from app.extensions import db


class JobPosting(db.Model):
    __tablename__ = "job_postings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    raw_text = db.Column(db.Text, nullable=False)
    parsed_json = db.Column(db.Text, nullable=True)
    vague = db.Column(db.Boolean, default=False, nullable=False)
    parse_error = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref=db.backref("job_postings", lazy="dynamic"))
