from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import select

from extensions import db
from models import Bettor


bettors_bp = Blueprint("bettors", __name__, url_prefix="/bettors")


@bettors_bp.get("/")
def list_bettors():
    bettors = db.session.scalars(select(Bettor).order_by(Bettor.name)).all()
    return render_template("bettors/list.html", bettors=bettors)


@bettors_bp.route("/new", methods=["GET", "POST"])
def create_bettor():
    if request.method == "POST":
        bettor = Bettor()
        if _populate_bettor(bettor):
            db.session.add(bettor)
            db.session.commit()
            flash("Bettor created.", "success")
            return redirect(url_for("bettors.list_bettors"))

    return render_template("bettors/form.html", bettor=None)


@bettors_bp.route("/<int:bettor_id>/edit", methods=["GET", "POST"])
def edit_bettor(bettor_id):
    bettor = db.get_or_404(Bettor, bettor_id)

    if request.method == "POST" and _populate_bettor(bettor):
        db.session.commit()
        flash("Bettor updated.", "success")
        return redirect(url_for("bettors.list_bettors"))

    return render_template("bettors/form.html", bettor=bettor)


def _populate_bettor(bettor):
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    notes = request.form.get("notes", "").strip()

    if not name:
        flash("Bettor name is required.", "danger")
        return False

    duplicate = db.session.scalar(
        select(Bettor).where(Bettor.name == name, Bettor.id != bettor.id)
    )
    if duplicate:
        flash("A bettor with that name already exists.", "danger")
        return False

    bettor.name = name
    bettor.phone = phone or None
    bettor.notes = notes or None
    return True
