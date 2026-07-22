from extensions import db


class Bettor(db.Model):
    """A person who can place bets on fights."""

    __tablename__ = "bettors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(40), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    def __repr__(self):
        return f"<Bettor {self.name}>"
