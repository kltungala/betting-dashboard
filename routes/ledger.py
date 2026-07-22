from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import select

from extensions import db
from models import Bettor, LedgerEntry


ledger_bp = Blueprint("ledger", __name__, url_prefix="/ledger")


@ledger_bp.get("/")
def list_ledger():
    entries = db.session.scalars(
        select(LedgerEntry).order_by(LedgerEntry.created_at.desc(), LedgerEntry.id.desc())
    ).all()
    balances = {bettor.id: bettor.balance for bettor in db.session.scalars(select(Bettor)).all()}
    return render_template("ledger/list.html", entries=entries, balances=balances)


@ledger_bp.route("/adjustment", methods=["GET", "POST"])
def create_adjustment():
    bettors = db.session.scalars(select(Bettor).order_by(Bettor.name)).all()
    if request.method == "POST":
        try:
            bettor = db.session.get(Bettor, int(request.form.get("bettor_id", "")))
            amount = Decimal(request.form.get("amount", ""))
        except (ValueError, InvalidOperation):
            flash("Select a bettor and enter a valid adjustment amount.", "danger")
        else:
            description = request.form.get("description", "").strip()
            if not bettor or amount == 0 or not description:
                flash("Bettor, non-zero amount, and description are required.", "danger")
            else:
                db.session.add(
                    LedgerEntry(
                        bettor=bettor,
                        entry_type="adjustment",
                        amount=amount.quantize(Decimal("0.01")),
                        description=description,
                    )
                )
                db.session.commit()
                flash("Adjustment recorded.", "success")
                return redirect(url_for("ledger.list_ledger"))
    return render_template("ledger/adjustment_form.html", bettors=bettors)
