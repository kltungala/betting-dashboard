from extensions import db


class Bet(db.Model):
    """A bettor's stake on one side of an open fight."""

    __tablename__ = "bets"

    id = db.Column(db.Integer, primary_key=True)
    fight_id = db.Column(db.Integer, db.ForeignKey("fights.id"), nullable=False)
    bettor_id = db.Column(db.Integer, db.ForeignKey("bettors.id"), nullable=False)
    fighter_side = db.Column(db.String(1), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    commission_percent = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    payment_type = db.Column(db.String(10), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="active")
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    fight = db.relationship("Fight", backref=db.backref("bets", lazy=True))
    bettor = db.relationship("Bettor", backref=db.backref("bets", lazy=True))

    def __repr__(self):
        return f"<Bet {self.id}>"
