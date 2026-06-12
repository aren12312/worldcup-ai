from __future__ import annotations

from typing import Any, Dict


def t(key: str, lang: str, **kwargs: Any) -> str:
    strings: Dict[str, Dict[str, str]] = {
        "draw_label": {"he": "תיקו", "en": "Draw"},
        "upset_low": {"he": "נמוך", "en": "low"},
        "upset_medium": {"he": "בינוני", "en": "medium"},
        "upset_high": {"he": "גבוה", "en": "high"},
        "confidence_high": {"he": "גבוהה", "en": "high"},
        "confidence_medium": {"he": "בינונית", "en": "medium"},
        "confidence_low": {"he": "נמוכה", "en": "low"},
        "data_quality_high": {
            "he": "גבוהה — מבוסס על משחקים אמיתיים מה-API",
            "en": "high — based on real matches from API",
        },
        "data_quality_medium": {
            "he": "בינונית — חלק מהנתונים ממסד מקומי",
            "en": "medium — partial data from local database",
        },
        "data_quality_low": {
            "he": "נמוכה — ודא ש-FOOTBALL_DATA_API_KEY מוגדר ב-GitHub Secrets",
            "en": "low — ensure FOOTBALL_DATA_API_KEY is set in GitHub Secrets",
        },
        "rec_draw": {
            "he": "משחק צמוד — סיכוי תיקו {draw:.0f}%, שתי הקבוצות שוות",
            "en": "Tight match — {draw:.0f}% draw, teams evenly matched",
        },
        "rec_win": {
            "he": "המלצה: {favorite} לנצח (ביטחון {confidence}) — יתרון xG של {xg_diff:.1f}",
            "en": "{favorite} to win (confidence: {confidence}) — xG edge {xg_diff:.1f}",
        },
        "unknown_team": {
            "he": "קבוצה לא מזוהה: {name}. נסה: ברזיל, צרפת, ארגנטינה",
            "en": "Unknown team: {name}. Try Brazil, France, Argentina",
        },
        "no_recent_data": {
            "he": "לא נמצאו משחקים אחרונים ב-API — הניתוח מבוסס על דירוגים",
            "en": "No recent API matches — analysis based on ratings",
        },
    }

    template = strings.get(key, {}).get(lang) or strings.get(key, {}).get("en", key)
    return template.format(**kwargs) if kwargs else template
