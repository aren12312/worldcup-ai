"""Key players database with availability status for national teams."""

KEY_PLAYERS = {
    "Brazil": [
        {"name": "Vinícius Júnior", "role": "FW", "impact": 95, "status": "available", "note_he": "מוביל התקפי, יוצר הזדמנויות מצד שמאל"},
        {"name": "Rodrygo", "role": "FW", "impact": 88, "status": "available", "note_he": "מהיר, מסיים מצוין באזור הרחבה"},
        {"name": "Casemiro", "role": "MF", "impact": 85, "status": "available", "note_he": "מאזן בין הגנה להתקפה"},
        {"name": "Alisson", "role": "GK", "impact": 90, "status": "available", "note_he": "שוער עולמי, יציבות defensivית"},
        {"name": "Neymar", "role": "FW", "impact": 82, "status": "doubtful", "note_he": "ספק — חזרה מפציעה, השפעה התקפית גבוהה אם fit"},
    ],
    "France": [
        {"name": "Kylian Mbappé", "role": "FW", "impact": 96, "status": "available", "note_he": "כוכב ההתקפה, מהירות וסיום"},
        {"name": "Antoine Griezmann", "role": "MF", "impact": 90, "status": "available", "note_he": "מוח המשחק, יצירתיות באמצע"},
        {"name": "Aurélien Tchouaméni", "role": "MF", "impact": 86, "status": "available", "note_he": "שליטה בקישור, הגנה על ההגנה"},
        {"name": "Mike Maignan", "role": "GK", "impact": 88, "status": "available", "note_he": "reflexes גבוהים, מנהיגות"},
        {"name": "Ousmane Dembélé", "role": "FW", "impact": 84, "status": "available", "note_he": "drift רחב, יוצר 1v1"},
    ],
    "Argentina": [
        {"name": "Lionel Messi", "role": "FW", "impact": 94, "status": "available", "note_he": "playmaker, set pieces, ניסיון"},
        {"name": "Lautaro Martínez", "role": "FW", "impact": 89, "status": "available", "note_he": "מסיים מצוין, movement באזור"},
        {"name": "Enzo Fernández", "role": "MF", "impact": 87, "status": "available", "note_he": "distribution, שליטה בקצב"},
        {"name": "Emiliano Martínez", "role": "GK", "impact": 88, "status": "available", "note_he": "penalty specialist, ביטחון"},
        {"name": "Ángel Di María", "role": "FW", "impact": 80, "status": "doubtful", "note_he": "ספק — חשוב במשחקים גדולים"},
    ],
    "England": [
        {"name": "Harry Kane", "role": "FW", "impact": 92, "status": "available", "note_he": "target man + playmaking"},
        {"name": "Bukayo Saka", "role": "FW", "impact": 88, "status": "available", "note_he": "1v1, crosses, goals"},
        {"name": "Declan Rice", "role": "MF", "impact": 87, "status": "available", "note_he": "הגנה על הקו האחורי"},
        {"name": "Jude Bellingham", "role": "MF", "impact": 91, "status": "available", "note_he": "box-to-box, late runs"},
        {"name": "Jordan Pickford", "role": "GK", "impact": 84, "status": "available", "note_he": "distribution + saves"},
    ],
    "Spain": [
        {"name": "Pedri", "role": "MF", "impact": 90, "status": "available", "note_he": "שליטה ויצירתיות"},
        {"name": "Lamine Yamal", "role": "FW", "impact": 88, "status": "available", "note_he": "talent צעיר, 1v1"},
        {"name": "Álvaro Morata", "role": "FW", "impact": 84, "status": "available", "note_he": "movement, finishing"},
        {"name": "Rodri", "role": "MF", "impact": 92, "status": "injured", "note_he": "פצוע — חוסר משמעותי באמצע"},
        {"name": "Unai Simón", "role": "GK", "impact": 85, "status": "available", "note_he": "יציבות בשער"},
    ],
    "Germany": [
        {"name": "Jamal Musiala", "role": "MF", "impact": 91, "status": "available", "note_he": "dribbling, between lines"},
        {"name": "Florian Wirtz", "role": "MF", "impact": 89, "status": "available", "note_he": "creativity, final third"},
        {"name": "Kai Havertz", "role": "FW", "impact": 84, "status": "available", "note_he": "link play, aerial"},
        {"name": "Manuel Neuer", "role": "GK", "impact": 83, "status": "available", "note_he": "sweeper keeper"},
        {"name": "Joshua Kimmich", "role": "MF", "impact": 88, "status": "available", "note_he": "balance, crosses"},
    ],
    "Portugal": [
        {"name": "Cristiano Ronaldo", "role": "FW", "impact": 86, "status": "available", "note_he": "סיום, set pieces, ניסיון"},
        {"name": "Bernardo Silva", "role": "MF", "impact": 89, "status": "available", "note_he": "technical control"},
        {"name": "Bruno Fernandes", "role": "MF", "impact": 88, "status": "available", "note_he": "key passes, shots"},
        {"name": "Rúben Dias", "role": "DF", "impact": 87, "status": "available", "note_he": "ארגון ההגנה"},
        {"name": "Diogo Costa", "role": "GK", "impact": 85, "status": "available", "note_he": "reflexes"},
    ],
    "Netherlands": [
        {"name": "Virgil van Dijk", "role": "DF", "impact": 90, "status": "available", "note_he": "leader at back"},
        {"name": "Memphis Depay", "role": "FW", "impact": 85, "status": "available", "note_he": "creativity upfront"},
        {"name": "Cody Gakpo", "role": "FW", "impact": 86, "status": "available", "note_he": "versatile attacker"},
        {"name": "Frenkie de Jong", "role": "MF", "impact": 88, "status": "doubtful", "note_he": "ספק — progression key"},
        {"name": "Xavi Simons", "role": "MF", "impact": 84, "status": "available", "note_he": "between lines threat"},
    ],
}

STATUS_HE = {
    "available": "צפוי לשחק",
    "doubtful": "ספק",
    "injured": "פצוע — לא צפוי",
    "suspended": "מושעה",
}


def get_key_players(team_name: str, lang: str = "he") -> list:
    players = KEY_PLAYERS.get(team_name, [])
    if not players:
        return [
            {
                "name": "N/A",
                "role": "-",
                "impact": 70,
                "status": "available",
                "status_label": "לא זמין במאגר",
                "note": "אין נתוני שחקנים לקבוצה זו",
            }
        ]

    result = []
    for p in players:
        status = p["status"]
        result.append(
            {
                "name": p["name"],
                "role": p["role"],
                "impact": p["impact"],
                "status": status,
                "status_label": STATUS_HE.get(status, status) if lang == "he" else status,
                "note": p.get("note_he", "") if lang == "he" else p.get("note_he", ""),
            }
        )
    return result
