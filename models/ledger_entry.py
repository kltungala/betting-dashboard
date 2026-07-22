from extensions import db


class LedgerEntry(db.Model):
    """An immutable balance movement for one bettor.

    Positive amounts increase what the bettor owes the house; negative amounts
    reduce it or represent money returned to the bettor.
    """

    __tablename__ = "ledger_entries"

    id = db.Column(db.Integer, primary_key=True)
    bettor_id = db.Column(db.Integer, db.ForeignKey("bettors.id"), nullable=False)
    entry_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    bet_id = db.Column(db.Integer, db.ForeignKey("bets.id"), nullable=True)
    payment_id = db.Column(db.Integer, db.ForeignKey("payments.id"), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    bettor = db.relationship("Bettor", backref=db.backref("ledger_entries", lazy=True))
    bet = db.relationship("Bet", backref=db.backref("ledger_entries", lazy=True))
    payment = db.relationship("Payment", backref=db.backref("ledger_entries", lazy=True))
