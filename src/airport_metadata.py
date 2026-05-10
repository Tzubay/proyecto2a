AIRPORT_METADATA = {
    # México
    "MEX": {"city": "Ciudad de México", "region": "Ciudad de México"},
    "CJS": {"city": "Ciudad Juárez", "region": "Chihuahua"},
    "AGU": {"city": "Aguascalientes", "region": "Aguascalientes"},
    "XAL": {"city": "Xalapa", "region": "Veracruz"},
    "TPQ": {"city": "Tepic", "region": "Nayarit"},
    "TGZ": {"city": "Tuxtla Gutiérrez", "region": "Chiapas"},
    "AZP": {"city": "Atizapán de Zaragoza", "region": "Estado de México"},
    "BHL": {"city": "Bahía de los Ángeles", "region": "Baja California"},
    "HUX": {"city": "Huatulco", "region": "Oaxaca"},
    "CSW": {"city": "Colorado do Oeste", "region": "Desconocida"},
    "CSL": {"city": "Cabo San Lucas", "region": "Baja California Sur"},
    "CNA": {"city": "Cananea", "region": "Sonora"},
    "CUN": {"city": "Cancún", "region": "Quintana Roo"},

    # España
    "MAD": {"city": "Madrid", "region": "Comunidad de Madrid"},
    "ALC": {"city": "Alicante", "region": "Comunidad Valenciana"},
    "LCG": {"city": "A Coruña", "region": "Galicia"},
    "GRO": {"city": "Girona", "region": "Cataluña"},
    "ABC": {"city": "Albacete", "region": "Castilla-La Mancha"},
    "AEI": {"city": "Algeciras", "region": "Andalucía"},

    # Japón
    "AGJ": {"city": "Aguni", "region": "Okinawa"},
    "AXT": {"city": "Akita", "region": "Akita"},
    "AXJ": {"city": "Amakusa", "region": "Kumamoto"},
    "ASJ": {"city": "Amami", "region": "Kagoshima"},
    "AOJ": {"city": "Aomori", "region": "Aomori"},
    "AKJ": {"city": "Asahikawa", "region": "Hokkaido"},
    "NJA": {"city": "Atsugi", "region": "Kanagawa"},
    "NGO": {"city": "Nagoya", "region": "Aichi"},
    "FUJ": {"city": "Gotō", "region": "Nagasaki"},
    "FKJ": {"city": "Fukui", "region": "Fukui"},
    "FUK": {"city": "Fukuoka", "region": "Fukuoka"},
    "FKS": {"city": "Fukushima", "region": "Fukushima"},
    "QFY": {"city": "Fukuyama", "region": "Hiroshima"},
    "QGU": {"city": "Gifu", "region": "Gifu"},
}


def get_airport_metadata(iata_code):
    return AIRPORT_METADATA.get(iata_code, {})
