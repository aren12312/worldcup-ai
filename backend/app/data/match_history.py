"""Curated recent results & H2H fallback when API tier is limited."""

RECENT_MATCHES = {
    "Brazil": [
        {"date": "2024-11-19", "outcome": "W", "score": "1-0", "opponent": "Uruguay", "competition": "World Cup Qualifiers"},
        {"date": "2024-11-14", "outcome": "D", "score": "1-1", "opponent": "Venezuela", "competition": "World Cup Qualifiers"},
        {"date": "2024-10-15", "outcome": "W", "score": "4-1", "opponent": "Chile", "competition": "World Cup Qualifiers"},
        {"date": "2024-10-10", "outcome": "W", "score": "2-0", "opponent": "Peru", "competition": "World Cup Qualifiers"},
        {"date": "2024-09-06", "outcome": "W", "score": "1-0", "opponent": "Ecuador", "competition": "World Cup Qualifiers"},
    ],
    "France": [
        {"date": "2024-11-19", "outcome": "W", "score": "4-1", "opponent": "Italy", "competition": "UEFA Nations League"},
        {"date": "2024-11-14", "outcome": "W", "score": "2-0", "opponent": "Israel", "competition": "UEFA Nations League"},
        {"date": "2024-10-14", "outcome": "D", "score": "0-0", "opponent": "Israel", "competition": "UEFA Nations League"},
        {"date": "2024-10-10", "outcome": "W", "score": "4-2", "opponent": "Belgium", "competition": "UEFA Nations League"},
        {"date": "2024-09-09", "outcome": "W", "score": "2-1", "opponent": "Belgium", "competition": "UEFA Nations League"},
    ],
    "Argentina": [
        {"date": "2024-11-19", "outcome": "W", "score": "1-0", "opponent": "Peru", "competition": "World Cup Qualifiers"},
        {"date": "2024-11-14", "outcome": "W", "score": "2-0", "opponent": "Paraguay", "competition": "World Cup Qualifiers"},
        {"date": "2024-10-15", "outcome": "W", "score": "6-0", "opponent": "Bolivia", "competition": "World Cup Qualifiers"},
        {"date": "2024-10-10", "outcome": "D", "score": "2-2", "opponent": "Venezuela", "competition": "World Cup Qualifiers"},
        {"date": "2024-09-05", "outcome": "W", "score": "3-0", "opponent": "Chile", "competition": "World Cup Qualifiers"},
    ],
    "England": [
        {"date": "2024-11-17", "outcome": "W", "score": "5-0", "opponent": "Ireland", "competition": "UEFA Nations League"},
        {"date": "2024-11-14", "outcome": "L", "score": "1-2", "opponent": "Greece", "competition": "UEFA Nations League"},
        {"date": "2024-10-13", "outcome": "W", "score": "3-1", "opponent": "Finland", "competition": "UEFA Nations League"},
        {"date": "2024-10-10", "outcome": "D", "score": "1-1", "opponent": "Greece", "competition": "UEFA Nations League"},
        {"date": "2024-09-10", "outcome": "W", "score": "2-0", "opponent": "Finland", "competition": "UEFA Nations League"},
    ],
    "Spain": [
        {"date": "2024-11-18", "outcome": "W", "score": "3-2", "opponent": "Switzerland", "competition": "UEFA Nations League"},
        {"date": "2024-11-15", "outcome": "W", "score": "4-0", "opponent": "Serbia", "competition": "UEFA Nations League"},
        {"date": "2024-10-15", "outcome": "W", "score": "1-0", "opponent": "Denmark", "competition": "UEFA Nations League"},
        {"date": "2024-10-12", "outcome": "D", "score": "1-1", "opponent": "Serbia", "competition": "UEFA Nations League"},
        {"date": "2024-09-08", "outcome": "W", "score": "2-1", "opponent": "Switzerland", "competition": "UEFA Nations League"},
    ],
    "Germany": [
        {"date": "2024-11-17", "outcome": "W", "score": "7-0", "opponent": "Bosnia", "competition": "UEFA Nations League"},
        {"date": "2024-11-14", "outcome": "D", "score": "1-1", "opponent": "Hungary", "competition": "UEFA Nations League"},
        {"date": "2024-10-14", "outcome": "W", "score": "1-0", "opponent": "Netherlands", "competition": "UEFA Nations League"},
        {"date": "2024-10-11", "outcome": "L", "score": "0-1", "opponent": "Netherlands", "competition": "UEFA Nations League"},
        {"date": "2024-09-07", "outcome": "W", "score": "2-1", "opponent": "Hungary", "competition": "UEFA Nations League"},
    ],
    "Portugal": [
        {"date": "2024-11-17", "outcome": "W", "score": "5-1", "opponent": "Poland", "competition": "UEFA Nations League"},
        {"date": "2024-11-14", "outcome": "W", "score": "3-1", "opponent": "Scotland", "competition": "UEFA Nations League"},
        {"date": "2024-10-15", "outcome": "W", "score": "3-0", "opponent": "Poland", "competition": "UEFA Nations League"},
        {"date": "2024-10-12", "outcome": "W", "score": "3-1", "opponent": "Scotland", "competition": "UEFA Nations League"},
        {"date": "2024-09-08", "outcome": "W", "score": "3-2", "opponent": "Scotland", "competition": "UEFA Nations League"},
    ],
    "Netherlands": [
        {"date": "2024-11-16", "outcome": "W", "score": "4-0", "opponent": "Hungary", "competition": "UEFA Nations League"},
        {"date": "2024-11-13", "outcome": "W", "score": "1-0", "opponent": "Bosnia", "competition": "UEFA Nations League"},
        {"date": "2024-10-14", "outcome": "L", "score": "0-1", "opponent": "Germany", "competition": "UEFA Nations League"},
        {"date": "2024-10-11", "outcome": "W", "score": "1-0", "opponent": "Germany", "competition": "UEFA Nations League"},
        {"date": "2024-09-07", "outcome": "W", "score": "2-1", "opponent": "Bosnia", "competition": "UEFA Nations League"},
    ],
}

H2H_MATCHES = {
    ("Brazil", "France"): [
        {"date": "1998-07-12", "home_team": "Brazil", "away_team": "France", "score": "0-3", "competition": "World Cup 1998 Final"},
        {"date": "1986-06-21", "home_team": "France", "away_team": "Brazil", "score": "1-1", "competition": "World Cup 1986"},
        {"date": "1974-06-15", "home_team": "Brazil", "away_team": "France", "score": "0-1", "competition": "World Cup 1974"},
        {"date": "1958-06-24", "home_team": "Brazil", "away_team": "France", "score": "5-2", "competition": "World Cup 1958 SF"},
        {"date": "1938-06-12", "home_team": "France", "away_team": "Brazil", "score": "1-1", "competition": "World Cup 1938 QF"},
    ],
    ("Argentina", "England"): [
        {"date": "2022-12-10", "home_team": "Argentina", "away_team": "Netherlands", "score": "2-2", "competition": "World Cup 2022"},
        {"date": "1998-06-30", "home_team": "Argentina", "away_team": "England", "score": "2-2", "competition": "World Cup 1998"},
        {"date": "1986-06-22", "home_team": "Argentina", "away_team": "England", "score": "2-1", "competition": "World Cup 1986"},
    ],
    ("Spain", "Germany"): [
        {"date": "2024-07-05", "home_team": "Spain", "away_team": "Germany", "score": "2-1", "competition": "Euro 2024"},
        {"date": "2010-07-07", "home_team": "Germany", "away_team": "Spain", "score": "0-1", "competition": "World Cup 2010"},
        {"date": "2008-06-29", "home_team": "Germany", "away_team": "Spain", "score": "0-1", "competition": "Euro 2008 Final"},
    ],
}


def get_curated_recent(team_name: str) -> list:
    return RECENT_MATCHES.get(team_name, [])


def get_curated_h2h(team1: str, team2: str) -> list:
    key = (team1, team2)
    rev = (team2, team1)
    if key in H2H_MATCHES:
        return H2H_MATCHES[key]
    if rev in H2H_MATCHES:
        return H2H_MATCHES[rev]
    return []
