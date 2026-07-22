from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import select

from extensions import db
from models import Bet, Fight
from services.ledger import record_payout_entry


fights_bp = Blueprint("fights", __name__, url_prefix="/fights")
MONEY = Decimal("0.01")


@fights_bp.get("/")
def list_fights():
    fights = db.session.scalars(select(Fight).order_by(Fight.fight_date.desc(), Fight.id.desc())).all()
    return render_template("fights/list.html", fights=fights)


@fights_bp.route("/new", methods=["GET", "POST"])
def create_fight():
    fight = Fight()
    if request.method == "POST" and _populate_fight(fight):
        db.session.add(fight)
        db.session.commit()
        flash("Fight created.", "success")
        return redirect(url_for("fights.detail_fight", fight_id=fight.id))
    return render_template("fights/form.html", fight=None, today=date.today().isoformat())


@fights_bp.get("/<int:fight_id>")
def detail_fight(fight_id):
    fight = db.get_or_404(Fight, fight_id)
    bets = db.session.scalars(select(Bet).where(Bet.fight_id == fight.id).order_by(Bet.id.desc())).all()
    return render_template("fights/detail.html", fight=fight, bets=bets)


@fights_bp.route("/<int:fight_id>/edit", methods=["GET", "POST"])
def edit_fight(fight_id):
    fight = db.get_or_404(Fight, fight_id)
    if fight.status != "open":
        flash("Only open fights can be edited.", "warning")
        return redirect(url_for("fights.detail_fight", fight_id=fight.id))
    if request.method == "POST" and _populate_fight(fight):
        db.session.commit()
        flash("Fight updated.", "success")
        return redirect(url_for("fights.detail_fight", fight_id=fight.id))
    return render_template("fights/form.html", fight=fight, today=date.today().isoformat())


@fights_bp.post("/<int:fight_id>/close")
def close_fight(fight_id):
    fight = db.get_or_404(Fight, fight_id)
    if fight.status == "open":
        fight.status = "closed"
        db.session.commit()
        flash("Fight closed. Bets can no longer be changed.", "success")
    return redirect(url_for("fights.detail_fight", fight_id=fight.id))


@fights_bp.post("/<int:fight_id>/delete")
def delete_fight(fight_id):
    fight = db.get_or_404(Fight, fight_id)
    for bet in list(fight.bets):
        for entry in list(bet.ledger_entries):
            db.session.delete(entry)
        db.session.delete(bet)
    db.session.delete(fight)
    db.session.commit()
    flash("Fight and all of its related bets and ledger entries were deleted.", "success")
    return redirect(url_for("fights.list_fights"))


@fights_bp.post("/<int:fight_id>/winner")
def declare_winner(fight_id):
    fight = db.get_or_404(Fight, fight_id)
    winner_side = request.form.get("winner_side")
    if fight.status == "settled":
        flash("This fight has already been settled.", "warning")
    elif winner_side not in {"A", "B"}:
        flash("Choose the winning side.", "danger")
    else:
        winning_bets = [
            bet for bet in fight.bets if bet.status == "active" and bet.fighter_side == winner_side
        ]
        if not winning_bets:
            flash("Cannot settle a fight without at least one bet on the winning side.", "danger")
        else:
            _settle_fight(fight, winner_side, winning_bets)
            db.session.commit()
            flash("Winner declared and payouts recorded.", "success")
    return redirect(url_for("fights.detail_fight", fight_id=fight.id))


def _populate_fight(fight):
    fighter_a = request.form.get("fighter_a", "").strip()
    fighter_b = request.form.get("fighter_b", "").strip()
    fight_date_value = request.form.get("fight_date", "").strip()
    if not fighter_a or not fighter_b or not fight_date_value:
        flash("Fighter A, Fighter B, and the fight date are required.", "danger")
        return False
    if fighter_a.casefold() == fighter_b.casefold():
        flash("Fighter A and Fighter B must be different.", "danger")
        return False
    try:
        fight_date = date.fromisoformat(fight_date_value)
    except ValueError:
        flash("Enter a valid fight date.", "danger")
        return False
    fight.fighter_a = fighter_a
    fight.fighter_b = fighter_b
    fight.fight_date = fight_date
    return True


def _settle_fight(fight, winner_side, winning_bets):
    losing_pool = sum(
        (bet.amount for bet in fight.bets if bet.status == "active" and bet.fighter_side != winner_side),
        Decimal("0.00"),
    )
    winning_pool = sum((bet.amount for bet in winning_bets), Decimal("0.00"))

    for bet in fight.bets:
        if bet.status != "active":
            continue
        if bet.fighter_side != winner_side:
            bet.status = "lost"
            bet.gross_winnings = Decimal("0.00")
            bet.commission_amount = Decimal("0.00")
            bet.net_profit = -bet.amount
            bet.total_returned = Decimal("0.00")
            continue

        gross = (bet.amount / winning_pool * losing_pool).quantize(MONEY, rounding=ROUND_HALF_UP)
        commission = (gross * bet.commission_percent / 100).quantize(MONEY, rounding=ROUND_HALF_UP)
        bet.gross_winnings = gross
        bet.commission_amount = commission
        bet.net_profit = gross - commission
        bet.total_returned = bet.amount + bet.net_profit
        bet.status = "won"
        record_payout_entry(bet)

    fight.winner_side = winner_side
    fight.status = "settled"
