import streamlit as st
from dotenv import load_dotenv
from services.odds_service import fetch_odds, parse_props, aggregate_and_rank
from db.database import SessionLocal, init_db
from db import models
from engine.correlation import compute_correlated_probability

load_dotenv()
init_db()

st.set_page_config(page_title="NBA Prop Analyzer", layout="wide")

tabs = st.tabs(["Dashboard", "Entry Builder", "History", "Settings"])

# Dashboard tab
with tabs[0]:
    st.header("Today's Best Picks")
    min_edge = st.slider("Minimum Edge", 0.0, 0.2, 0.05, 0.01)
    top_n = st.number_input("Top N", 1, 50, 10)
    if st.button("Scan"):
        data = fetch_odds()
        props = parse_props(data)
        candidates = aggregate_and_rank(props, min_edge=min_edge)
        st.session_state.candidates = candidates[:top_n]
    if "candidates" in st.session_state:
        for idx, c in enumerate(st.session_state.candidates, start=1):
            st.write(f"{idx}. **{c['player']}** {c['market']} {c['side']} {c['line']}  \n"
                     f"Model prob: {c['model_prob']:.2f} | Market prob: {c['market_prob']:.2f} | Edge: {c['edge']:.2f}")
            if st.button(f"Save pick {idx}", key=f"save_{idx}"):
                session = SessionLocal()
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
                st.success("Pick saved.")

# Entry Builder tab
with tabs[1]:
    st.header("Build an Entry")
    session = SessionLocal()
    saved_picks = session.query(models.Pick).filter(models.Pick.result.is_(None)).all()
    selected_ids = st.multiselect("Select legs (2–5)", [p.id for p in saved_picks])
    payout = st.number_input("Payout multiplier", 0.0, 10.0, 3.0)
    if st.button("Evaluate Entry"):
        if not (2 <= len(selected_ids) <= 5):
            st.error("Please select between 2 and 5 legs.")
        else:
            probs = []
            legs_info = []
            for pid in selected_ids:
                pick = session.query(models.Pick).filter(models.Pick.id == pid).first()
                probs.append(pick.model_prob)
                legs_info.append((pick.player_id or pick.player, pick.game_id))
            combined_prob = compute_correlated_probability(probs, legs_info)
            fair_odds = 1 / combined_prob if combined_prob > 0 else None
            ev = combined_prob * payout - 1
            st.write(f"Combined probability: {combined_prob:.3f}")
            if fair_odds:
                st.write(f"Fair odds: {fair_odds:.2f}")
            st.write(f"Expected value: {ev:.3f}")

# History tab
with tabs[2]:
    st.header("History / Tracking")
    session = SessionLocal()
    picks = session.query(models.Pick).all()
    for pick in picks:
        result = pick.result or "pending"
        st.write(f"{pick.timestamp.date()} – {pick.player} {pick.market} {pick.side} {pick.line} "
                 f"Model: {pick.model_prob:.2f} | Market: {pick.market_prob:.2f} | Edge: {pick.edge:.2f} | Result: {result}")

    if st.button("Update Results"):
        from services.results_service import fetch_game_results
        updated = 0
        for pick in picks:
            if pick.result is not None:
                continue
            result = fetch_game_results(pick.game_id)
            if not result:
                continue
            # TODO: parse box score; leave as pending
            pick.result = None
            updated += 1
        session.commit()
        st.success(f"Updated {updated} picks (best effort).")

# Settings tab
with tabs[3]:
    st.header("Settings")
    st.markdown("Adjust correlation coefficients for your model.")
    same_player_corr = st.slider("Same player correlation", 0.0, 1.0, 0.3, 0.05)
    same_game_corr = st.slider("Same game correlation", 0.0, 1.0, 0.1, 0.05)
    st.session_state.same_player_corr = same_player_corr
    st.session_state.same_game_corr = same_game_corr
    st.info("These settings take effect when computing correlated probabilities in the Entry Builder.")
