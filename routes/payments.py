from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import select

from extensions import db
from models import Bettor, LedgerEntry, Payment


payments_bp = Blueprint("payments", __name__, url_prefix="/payments")


@payments_bp.get("/")
def list_payments():
    payments = db.session.scalars(select(Payment).order_by(Payment.payment_date.desc(), Payment.id.desc())).all()
    return render_template("payments/list.html", payments=payments)


@payments_bp.route("/new", methods=["GET", "POST"])
def create_payment():
    bettors = db.session.scalars(select(Bettor).order_by(Bettor.name)).all()
    if request.method == "POST":
        try:
            bettor = db.session.get(Bettor, int(request.form.get("bettor_id", "")))
            amount = Decimal(request.form.get("amount", ""))
            payment_date = date.fromisoformat(request.form.get("payment_date", ""))
        except (ValueError, InvalidOperation):
            flash("Select a bettor and enter a valid amount and date.", "danger")
        else:
            if not bettor or amount <= 0:
                flash("Select a bettor and enter an amount greater than zero.", "danger")
            else:
                payment = Payment(
                    bettor=bettor,
                    amount=amount.quantize(Decimal("0.01")),
                    payment_date=payment_date,
                    notes=request.form.get("notes", "").strip() or None,
                )
                db.session.add(payment)
                db.session.flush()
                db.session.add(
                    LedgerEntry(
                        bettor=bettor,
                        payment=payment,
                        entry_type="payment",
                        amount=-payment.amount,
                        description="Payment received",
                    )
                )
                db.session.commit()
                flash("Payment recorded.", "success")
                return redirect(url_for("payments.list_payments"))
    return render_template("payments/form.html", bettors=bettors, today=date.today().isoformat())
