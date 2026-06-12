def compute_expected_goals(
    team: dict,
    opponent: dict,
    *,
    home_advantage: float = 1.0,
) -> float:
    """Derive expected goals from attack/defense ratings and recent form."""
    attack = team["attack"] / 100.0
    defense_factor = 1.15 - (opponent["defense"] / 250.0)
    form = 0.55 + team.get("form", 0.7) * 0.45

    xg = attack * defense_factor * form * 2.8 * home_advantage
    return round(max(0.55, min(3.2, xg)), 2)


def compute_upset_risk(probabilities: dict) -> str:
    favorite = max(
        probabilities["team1_win"],
        probabilities["team2_win"],
    )
    if favorite >= 55:
        return "low"
    if favorite >= 38:
        return "medium"
    return "high"


def build_recommendation(
    team1: str,
    team2: str,
    probabilities: dict,
    expected_goals: dict,
) -> str:
    t1_win = probabilities["team1_win"]
    t2_win = probabilities["team2_win"]
    draw = probabilities["draw"]

    if abs(t1_win - t2_win) < 8 and draw >= 25:
        return f"Draw or tight match — both teams near equal strength ({draw:.0f}% draw chance)"

    if t1_win > t2_win:
        favorite = team1
        margin = t1_win - t2_win
        xg_diff = expected_goals[team1] - expected_goals[team2]
    else:
        favorite = team2
        margin = t2_win - t1_win
        xg_diff = expected_goals[team2] - expected_goals[team1]

    confidence = "high" if margin >= 20 else "medium" if margin >= 10 else "low"
    return (
        f"{favorite} to win (confidence: {confidence}) — "
        f"expected goals edge of {abs(xg_diff):.1f}"
    )
