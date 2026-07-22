from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for

from extensions import db
from models import Fight


fights_bp = Blueprint("fights", __name__, url_prefix="/fights")


@fights_bp.get("/")
def list_fights():
    fights = Fight.query.order_by(Fight.fight_date.desc(), Fight.id.desc()).all()
    return render_template("fights/list.html", fights=fights)


@fights_bp.route("/new", methods=["GET", "POST"])
def create_fight():
    if request.method == "POST":
        fighter_a = request.form.get("fighter_a", "").strip()
        fighter_b = request.form.get("fighter_b", "").strip()
        fight_date_value = request.form.get("fight_date", "").strip()

        if not fighter_a or not fighter_b or not fight_date_value:
            flash("Fighter A, Fighter B, and the fight date are required.", "danger")
        elif fighter_a.casefold() == fighter_b.casefold():
            flash("Fighter A and Fighter B must be different.", "danger")
        else:
            try:
                fight_date = date.fromisoformat(fight_date_value)
            except ValueError:
                flash("Enter a valid fight date.", "danger")
            else:
                fight = Fight(
                    fighter_a=fighter_a,
                    fighter_b=fighter_b,
                    fight_date=fight_date,
                )
                db.session.add(fight)
                db.session.commit()
                flash("Fight created.", "success")
                return redirect(url_for("fights.list_fights"))

    return render_template("fights/form.html", today=date.today().isoformat())
