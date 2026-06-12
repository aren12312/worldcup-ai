from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import httpx

from backend.app.services.i18n import t

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _format_recent_matches(team_name: str, matches: List[dict], lang: str) -> List[str]:
    lines = []
    for match in matches[:5]:
        outcome = match.get("outcome", "?")
        if lang == "he":
            outcome_map = {"W": "נצ'", "D": "תיקו", "L": "הפסד"}
            outcome = outcome_map.get(outcome, outcome)
        lines.append(
            f"{match.get('date')} | {outcome} {match.get('score')} vs {match.get('opponent')} "
            f"({match.get('competition', '')})"
        )
    return lines


def _format_h2h(matches: List[dict], lang: str) -> List[str]:
    lines = []
    for match in matches[:5]:
        lines.append(
            f"{match.get('date')} | {match.get('home_team')} {match.get('score')} "
            f"{match.get('away_team')} ({match.get('competition', '')})"
        )
    return lines


def _h2h_summary(team1: str, team2: str, h2h: List[dict], lang: str) -> str:
    if not h2h:
        return t("no_recent_data", lang)

    t1_wins = t2_wins = draws = 0
    for match in h2h:
        home = match.get("home_team", "")
        score = match.get("score", "0-0")
        try:
            hg, ag = score.split("-")
            hg, ag = int(hg), int(ag)
        except ValueError:
            continue

        if hg == ag:
            draws += 1
        elif (home == team1 and hg > ag) or (home == team2 and ag > hg):
            if home == team1:
                t1_wins += 1
            else:
                t2_wins += 1
        else:
            if home == team1:
                t2_wins += 1
            else:
                t1_wins += 1

    if lang == "he":
        return (
            f"Head-to-Head אחרון ({len(h2h)} משחקים): "
            f"{team1} {t1_wins} נצ' | תיקו {draws} | {team2} {t2_wins} נצ'"
        )
    return f"Recent H2H ({len(h2h)}): {team1} {t1_wins}W | Draw {draws} | {team2} {t2_wins}W"


async def generate_analysis(
    team1: str,
    team2: str,
    team1_data: dict,
    team2_data: dict,
    expected_goals: dict,
    probabilities: dict,
    recommendation: str,
    context: dict,
    lang: str = "he",
) -> dict:
    recent_form = {
        team1: _format_recent_matches(team1, team1_data.get("recent_matches", []), lang),
        team2: _format_recent_matches(team2, team2_data.get("recent_matches", []), lang),
    }
    head_to_head = _format_h2h(context.get("head_to_head", []), lang)
    h2h_summary = _h2h_summary(team1, team2, context.get("head_to_head", []), lang)

    if OPENAI_API_KEY:
        llm = await _llm_analysis(
            team1,
            team2,
            team1_data,
            team2_data,
            expected_goals,
            probabilities,
            recommendation,
            recent_form,
            head_to_head,
            h2h_summary,
            lang,
        )
        if llm:
            llm["recent_form"] = recent_form
            llm["head_to_head"] = head_to_head
            llm["h2h_summary"] = h2h_summary
            return llm

    return _fallback_analysis(
        team1,
        team2,
        team1_data,
        team2_data,
        expected_goals,
        probabilities,
        recommendation,
        recent_form,
        head_to_head,
        h2h_summary,
        lang,
    )


async def _llm_analysis(
    team1: str,
    team2: str,
    team1_data: dict,
    team2_data: dict,
    expected_goals: dict,
    probabilities: dict,
    recommendation: str,
    recent_form: dict,
    head_to_head: List[str],
    h2h_summary: str,
    lang: str,
) -> Optional[dict]:
    lang_instruction = "Respond entirely in Hebrew." if lang == "he" else "Respond in English."

    dossier = {
        "team1": team1,
        "team2": team2,
        "team1_recent": recent_form.get(team1, []),
        "team2_recent": recent_form.get(team2, []),
        "head_to_head": head_to_head,
        "h2h_summary": h2h_summary,
        "team1_stats": {
            "attack": team1_data.get("attack"),
            "defense": team1_data.get("defense"),
            "form": team1_data.get("form"),
            "avg_scored": team1_data.get("avg_goals_scored"),
            "avg_conceded": team1_data.get("avg_goals_conceded"),
        },
        "team2_stats": {
            "attack": team2_data.get("attack"),
            "defense": team2_data.get("defense"),
            "form": team2_data.get("form"),
            "avg_scored": team2_data.get("avg_goals_scored"),
            "avg_conceded": team2_data.get("avg_goals_conceded"),
        },
        "expected_goals": expected_goals,
        "probabilities": probabilities,
        "recommendation": recommendation,
    }

    prompt = f"""You are an elite World Cup football analyst. {lang_instruction}
Use ONLY the real match data in the dossier below. Do not invent scores or events.

DOSSIER:
{json.dumps(dossier, ensure_ascii=False, indent=2)}

Return JSON with this exact structure:
{{
  "summary": "2-3 sentence executive summary",
  "key_factors": ["factor1", "factor2", "factor3", "factor4", "factor5"],
  "detailed": "A detailed paragraph (5-8 sentences) citing specific recent results and H2H",
  "analysis": ["bullet1", "bullet2", "bullet3", "bullet4", "bullet5"]
}}"""

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENAI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"},
                },
            )

        if response.status_code != 200:
            return None

        content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        if parsed.get("analysis") and parsed.get("summary"):
            return parsed
    except (KeyError, json.JSONDecodeError, httpx.HTTPError):
        return None

    return None


def _fallback_analysis(
    team1: str,
    team2: str,
    team1_data: dict,
    team2_data: dict,
    expected_goals: dict,
    probabilities: dict,
    recommendation: str,
    recent_form: dict,
    head_to_head: List[str],
    h2h_summary: str,
    lang: str,
) -> dict:
    favorite = team1 if probabilities["team1_win"] >= probabilities["team2_win"] else team2
    fav_prob = max(probabilities["team1_win"], probabilities["team2_win"])

    if lang == "he":
        bullets = []

        if recent_form.get(team1):
            bullets.append(f"📈 {team1} — 5 משחקים אחרונים: " + " | ".join(recent_form[team1][:3]))
        else:
            bullets.append(
                f"📈 {team1} — ממוצע {team1_data.get('avg_goals_scored', 'N/A')} שערים למשחק "
                f"(הגנה {team1_data['defense']}/100)"
            )

        if recent_form.get(team2):
            bullets.append(f"📈 {team2} — 5 משחקים אחרונים: " + " | ".join(recent_form[team2][:3]))
        else:
            bullets.append(
                f"📈 {team2} — ממוצע {team2_data.get('avg_goals_scored', 'N/A')} שערים למשחק "
                f"(הגנה {team2_data['defense']}/100)"
            )

        if head_to_head:
            bullets.append(f"🔄 {h2h_summary}")
            bullets.append(f"   אחרון: {head_to_head[0]}")
        else:
            bullets.append("🔄 אין נתוני H2H עדכניים מה-API")

        bullets.append(
            f"⚽ xG צפוי: {team1} {expected_goals[team1]} | {team2} {expected_goals[team2]}"
        )
        bullets.append(
            f"🎯 המודל מעדיף {favorite} ({fav_prob:.0f}% ניצחון, "
            f"{probabilities['draw']:.0f}% תיקו)"
        )

        summary = (
            f"ניתוח {team1} נגד {team2}: {recommendation}. "
            f"הסתברויות — {team1} {probabilities['team1_win']}%, "
            f"תיקו {probabilities['draw']}%, {team2} {probabilities['team2_win']}%."
        )

        detailed = (
            f"{summary} "
            f"{team1} מציגה טופס {team1_data.get('form_string') or 'לא ידוע'} "
            f" עם יכולת התקפית {team1_data['attack']}/100. "
            f"{team2} בטופס {team2_data.get('form_string') or 'לא ידוע'} "
            f" עם הגנה {team2_data['defense']}/100. "
            f"{h2h_summary if head_to_head else t('no_recent_data', lang)}"
        )
    else:
        bullets = [
            f"{team1} xG {expected_goals[team1]} | {team2} xG {expected_goals[team2]}",
            f"Model favors {favorite} at {fav_prob:.0f}%",
            h2h_summary,
        ]
        summary = recommendation
        detailed = summary

    return {
        "summary": summary,
        "key_factors": bullets[:5],
        "detailed": detailed,
        "analysis": bullets,
        "recent_form": recent_form,
        "head_to_head": head_to_head,
        "h2h_summary": h2h_summary,
    }
