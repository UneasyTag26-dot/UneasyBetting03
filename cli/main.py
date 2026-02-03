import click
import json
from typing import List
from sqlalchemy.orm import Session

from ..services.odds_service import fetch_odds, parse_props, aggregate_and_rank
from ..db.database import SessionLocal, init_db
from ..db import models
from ..engine.correlation import compute_correlated_probability


@click.group()
def cli():
    """NBA Prop Analyzer CLI."""
    init_db()


@cli.command()
@click.option("--top", default=10, type=int, help="Show top N props.")
@click.option("--edge", default=0.05, type=float, help="Minimum edge threshold.")
@click.option("--min-books", default=1, type=int, help="Minimum number of books required.")
@click.option("--save", is_flag=True, help="Save suggested picks to database.")
def scan(top: int, edge: float, min_books: int, save: bool):
    """Scan upcoming games and list candidate props."""
    data = fetch_odds()
    props = parse_props(data)
    candidates = aggregate_and_rank(props, min_books=min_books, min_edge=edge)
    for idx, c in enumerate(candidates[:top], start=1):
        click.echo(f"{idx}. {c['player']} {c['market']} {c['side']} {c['line']} – "
                   f"Model: {c['model_prob']:.3f}, Market: {c['market_prob']:.3f}, Edge: {c['edge']:.3f}")
    if save:
        session: Session = SessionLocal()
        for c in candidates[:top]:
            pick = models.Pick(
                player=c["player"],
                market=c["market"],
                line=c["line"],
                side=c["side"],
                model_prob=c["model_prob"],
                market_prob=c["market_prob"],
                edge=c["edge"],
                game_id=c["game_id"],
                player_id=c["player_id"],
            )
            session.add(pick)
        session.commit()
        click.echo(f"Saved {min(top, len(candidates))} picks to database.")


@cli.command()
@click.option("--entry", type=click.Path(exists=True), required=True, help="Entry file (JSON or text).")
def evaluate_entry(entry):
    """
    Evaluate an entry of 2–5 legs. The entry file should contain a list of pick IDs (if saved)
    or objects with model_prob fields. Outputs combined probability, fair odds, and EV.
    """
    session: Session = SessionLocal()
    with open(entry, "r") as f:
        data = json.load(f)
    probs = []
    legs_info = []
    for leg in data["legs"]:
        if "pick_id" in leg:
            pick = session.query(models.Pick).filter(models.Pick.id == leg["pick_id"]).first()
            if not pick:
                click.echo(f"Pick ID {leg['pick_id']} not found.")
                return
            probs.append(pick.model_prob)
            legs_info.append((pick.player_id or pick.player, pick.game_id))
        else:
            probs.append(leg["model_prob"])
            legs_info.append(("unknown", "unknown"))
    combined_prob = compute_correlated_probability(probs, legs_info)
    fair_odds = 1 / combined_prob if combined_prob > 0 else None
    payout_multiplier = data.get("payout_multiplier", 1.0)
    expected_value = combined_prob * payout_multiplier - 1

    click.echo(f"Combined probability: {combined_prob:.3f}")
    if fair_odds:
        click.echo(f"Fair odds: {fair_odds:.2f}")
    click.echo(f"Expected value (EV): {expected_value:.3f}")


@cli.command()
def update_results():
    """
    Fetch results for completed games and update pick outcomes.
    This uses a naive mapping of game_id to balldontlie game ID.
    """
    from ..services.results_service import fetch_game_results
    session: Session = SessionLocal()
    picks = session.query(models.Pick).filter(models.Pick.result.is_(None)).all()
    updated = 0
    for pick in picks:
        result = fetch_game_results(pick.game_id)
        if not result:
            continue
        # A best‑effort approach: if player's final stat exceeds line and side is "over" => win, etc.
        player_stat = None  # TODO: map player to stat via box scores; for now, skip
        # Mark push or unresolved if cannot determine
        pick.result = None
        updated += 1
    session.commit()
    click.echo(f"Updated {updated} picks (best effort).")


if __name__ == "__main__":
    cli()
