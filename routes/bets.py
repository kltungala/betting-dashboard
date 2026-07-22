from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import select

from extensions import db
from models import Bet, Bettor, Fight


bets_bp = Blueprint("bets", __name__, url_prefix="/bets")


@bets_bp.get("/")
def list_bets():
    bets = db.session.scalars(select(Bet).order_by(Bet.created_at.desc(), Bet.id.desc())).all()
    return render_template("bets/list.html", bets=bets)


@bets_bp.route("/new", methods=["GET", "POST"])
def create_bet():
    fights = _open_fights()
    bettors = _bettors()

    if request.method == "POST":
        bet = Bet()
        if _populate_bet(bet):
            db.session.add(bet)
            db.session.commit()
            flash("Bet created.", "success")
            return redirect(url_for("bets.list_bets"))

    return render_template("bets/form.html", bet=None, fights=fights, bettors=bettors)


@bets_bp.route("/<int:bet_id>/edit", methods=["GET", "POST"])
def edit_bet(bet_id):
    bet = db.get_or_404(Bet, bet_id)
    if bet.fight.status != "open":
        flash("Bets cannot be edited after a fight closes.", "warning")
        return redirect(url_for("bets.list_bets"))

    if request.method == "POST" and _populate_bet(bet):
        db.session.commit()
        flash("Bet updated.", "success")
        return redirect(url_for("bets.list_bets"))

    return render_template("bets/form.html", bet=bet, fights=_open_fights(), bettors=_bettors())


def _open_fights():
    return db.session.scalars(
        select(Fight).where(Fight.status == "open").order_by(Fight.fight_date.desc())
    ).all()


def _bettors():
    return db.session.scalars(select(Bettor).order_by(Bettor.name)).all()


def _populate_bet(bet):
    try:
        fight_id = int(request.form.get("fight_id", ""))
        bettor_id = int(request.form.get("bettor_id", ""))
        amount = Decimal(request.form.get("amount", ""))
        commission_percent = Decimal(request.form.get("commission_percent", ""))
    except (ValueError, InvalidOperation):
        flash("Select a fight and bettor, then enter valid numeric values.", "danger")
        return False

    fight = db.session.get(Fight, fight_id)
    bettor = db.session.get(Bettor, bettor_id)
    fighter_side = request.form.get("fighter_side")
    payment_type = request.form.get("payment_type")

    if not fight or fight.status != "open":
        flash("Select an open fight.", "danger")
        return False
    if not bettor:
        flash("Select a valid bettor.", "danger")
        return False
    if fighter_side not in {"A", "B"}:
        flash("Choose Fighter A or Fighter B.", "danger")
        return False
    if amount <= 0:
        flash("Bet amount must be greater than zero.", "danger")
        return False
    if not 0 <= commission_percent <= 100:
        flash("Commission must be between 0 and 100 percent.", "danger")
        return False
    if payment_type not in {"cash", "credit"}:
        flash("Choose cash or credit.", "danger")
        return False

    bet.fight = fight
    bet.bettor = bettor
    bet.fighter_side = fighter_side
    bet.amount = amount.quantize(Decimal("0.01"))
    bet.commission_percent = commission_percent.quantize(Decimal("0.01"))
    bet.payment_type = payment_type
    bet.notes = request.form.get("notes", "").strip() or None
    return True
