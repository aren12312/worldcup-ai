"""Hebrew team name aliases → English canonical names."""

HEBREW_ALIASES = {
    "ברזיל": "Brazil",
    "brazil": "Brazil",
    "צרפת": "France",
    "france": "France",
    "ארגנטינה": "Argentina",
    "argentina": "Argentina",
    "אנגליה": "England",
    "england": "England",
    "ספרד": "Spain",
    "spain": "Spain",
    "גרמניה": "Germany",
    "germany": "Germany",
    "פורטוגל": "Portugal",
    "portugal": "Portugal",
    "הולנד": "Netherlands",
    "netherlands": "Netherlands",
    "בלגיה": "Belgium",
    "belgium": "Belgium",
    "איטליה": "Italy",
    "italy": "Italy",
    "קרואטיה": "Croatia",
    "croatia": "Croatia",
    "אורוגוואי": "Uruguay",
    "uruguay": "Uruguay",
    "קולומביה": "Colombia",
    "colombia": "Colombia",
    "מקסיקו": "Mexico",
    "mexico": "Mexico",
    'ארה"ב': "USA",
    "ארהב": "USA",
    "usa": "USA",
    "יפן": "Japan",
    "japan": "Japan",
    "מרוקו": "Morocco",
    "morocco": "Morocco",
    "סנגל": "Senegal",
    "senegal": "Senegal",
    "שווייץ": "Switzerland",
    "switzerland": "Switzerland",
    "דנמרק": "Denmark",
    "denmark": "Denmark",
    "פולין": "Poland",
    "poland": "Poland",
    "אוסטרליה": "Australia",
    "australia": "Australia",
    "דרום קוריאה": "South Korea",
    "south korea": "South Korea",
    "קנדה": "Canada",
    "canada": "Canada",
    "ישראל": "Israel",
    "israel": "Israel",
    "ניגריה": "Nigeria",
    "nigeria": "Nigeria",
    "מצרים": "Egypt",
    "egypt": "Egypt",
    "טורקיה": "Turkey",
    "turkey": "Turkey",
    "אקוador": "Ecuador",
    "ecuador": "Ecuador",
    "צ'ile": "Chile",
    "chile": "Chile",
}

HEBREW_TEAM_NAMES = {
    "Brazil": "ברזיל",
    "France": "צרפת",
    "Argentina": "ארגנטינה",
    "England": "אנגליה",
    "Spain": "ספרד",
    "Germany": "גרמניה",
    "Portugal": "פורטוגל",
    "Netherlands": "הולנד",
    "Belgium": "בלגיה",
    "Italy": "איטליה",
    "Croatia": "קרואטיה",
    "Uruguay": "אורוגוואי",
    "Colombia": "קולומביה",
    "Mexico": "מקסיקו",
    "USA": 'ארה"ב',
    "Japan": "יפן",
    "Morocco": "מרוקו",
    "Senegal": "סנגל",
    "Switzerland": "שווייץ",
    "Denmark": "דנמרק",
    "Poland": "פולין",
    "Australia": "אוסטרליה",
    "South Korea": "דרום קוריאה",
    "Canada": "קנדה",
    "Israel": "ישראל",
    "Nigeria": "ניגריה",
    "Egypt": "מצרים",
    "Turkey": "טורקיה",
    "Ecuador": "אקוador",
    "Chile": "צ'ile",
}


def normalize_team_input(name: str) -> str:
    cleaned = name.strip()
    if cleaned in HEBREW_ALIASES:
        return HEBREW_ALIASES[cleaned]
    lowered = cleaned.lower()
    if lowered in HEBREW_ALIASES:
        return HEBREW_ALIASES[lowered]
    return cleaned


def display_team_name(english_name: str, lang: str) -> str:
    if lang == "he":
        return HEBREW_TEAM_NAMES.get(english_name, english_name)
    return english_name
