COUNTRIES_ES = {
    "méxico": "MX",
    "mexico": "MX",
    "estados unidos": "US",
    "canadá": "CA",
    "canada": "CA",
    "españa": "ES",
    "espana": "ES",
    "brasil": "BR",
    "argentina": "AR",
    "colombia": "CO",
    "chile": "CL",
    "perú": "PE",
    "peru": "PE",
    "francia": "FR",
    "alemania": "DE",
    "italia": "IT",
    "reino unido": "GB",
    "japón": "JP",
    "japon": "JP"
}


def get_country_code(country_name):
    normalized = country_name.strip().lower()

    if normalized not in COUNTRIES_ES:
        return None

    return COUNTRIES_ES[normalized]
