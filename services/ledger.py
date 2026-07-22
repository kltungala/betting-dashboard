from decimal import Decimal

from sqlalchemy import delete

from extensions import db
from models import LedgerEntry


def record_bet_entries(bet):
    """Replace draft ledger entries when an open bet is created or edited."""
    db.session.execute(
        delete(LedgerEntry).where(
            LedgerEntry.bet_id == bet.id,
            LedgerEntry.entry_type.in_(["bet", "credit"]),
        )
    )
    db.session.add(
        LedgerEntry(
            bettor=bet.bettor,
            bet=bet,
            entry_type="bet",
            amount=Decimal("0.00"),
            description=f"Bet on {bet.fight.fighter_a} vs {bet.fight.fighter_b}",
        )
    )
    if bet.payment_type == "credit":
        db.session.add(
            LedgerEntry(
                bettor=bet.bettor,
                bet=bet,
                entry_type="credit",
                amount=bet.amount,
                description=f"Credit bet on {bet.fight.fighter_a} vs {bet.fight.fighter_b}",
            )
        )


def record_payout_entry(bet):
    db.session.add(
        LedgerEntry(
            bettor=bet.bettor,
            bet=bet,
            entry_type="payout",
            amount=-bet.net_profit,
            description=f"Payout for {bet.fight.fighter_a} vs {bet.fight.fighter_b}",
        )
    )


def record_loss_entry(bet):
    db.session.add(
        LedgerEntry(
            bettor=bet.bettor,
            bet=bet,
            entry_type="loss",
            amount=bet.amount,
            description=f"Loss on {bet.fight.fighter_a} vs {bet.fight.fighter_b}",
        )
    )
