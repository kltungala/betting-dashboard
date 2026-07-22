from datetime import date

from extensions import db


class Fight(db.Model):
    """A scheduled match between two fighters."""

    __tablename__ = "fights"

    id = db.Column(db.Integer, primary_key=True)
    fighter_a = db.Column(db.String(120), nullable=False)
    fighter_b = db.Column(db.String(120), nullable=False)
    fight_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), nullable=False, default="open")
    winner_side = db.Column(db.String(1), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    def __repr__(self):
        return f"<Fight {self.fighter_a} vs {self.fighter_b}>"
