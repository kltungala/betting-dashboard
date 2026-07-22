from extensions import db


class Payment(db.Model):
    """A payment made by a bettor against their outstanding balance."""

    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    bettor_id = db.Column(db.Integer, db.ForeignKey("bettors.id"), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    bettor = db.relationship("Bettor", backref=db.backref("payments", lazy=True))
