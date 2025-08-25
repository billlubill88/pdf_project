# configs/config_search.py

# Общий SEARCH_CONFIG для всех форматов (используется по умолчанию для "GOST", "CURSIV", "DOSYL", "CHARTER" если нет специфических конфигов)
SEARCH_CONFIG = {
    "all": {
        "title_blocks": [
            {
                "block": 3,
                "name": "SHIPPER",
                "search_phrase": ["SHIPPER", "EXPORTER", "EXPEDITEUR", "EMBARCADOR", "EXPORTADOR"],
                "minus_phrase": [],
            },
            {
                "block": 4,
                "name": "CONSIGNEE",
                "search_phrase": ["CONSIGNEE", "RECEIVER", "CONSIGNATARIO"],
                "minus_phrase": [],
            },
            {
                "block": 6,
                "name": "VESSEL",
                "search_phrase": ["VESSEL", "VOYAGE", "NAVIRE", "EMBARCACION", "BUQUE"],
                "minus_phrase": [],
            },
            {
                "block": 8,
                "name": "PORT DISCHARGE",
                "search_phrase": ["PORT OF DISCHARGE", "PORT OF UNLOADING", "PUERTO DE DESTINO", "Порт разгрузки"],
                "minus_phrase": [],
            },
            {
                "block": 11,
                "name": "SHIPPED ON BOARD DATE",
                "search_phrase": ["PLACE AND DATE OF ISSUE", "DATE OF SHIPMENT", "EMBARQUE", "ISSUED AT"],
                "minus_phrase": [],
            }
        ],
        "rider_blocks": [
            {
                "block": 13,
                "name": "BOXES",
                "search_phrase": ["BOXES", "CAJAS", "COLIS", "EMBALAJE"],
                "minus_phrase": [],
            },
            {
                "block": 14,
                "name": "PER BOX",
                "search_phrase": ["PER BOX", "KGS/BOX", "POR CAJA"],
                "minus_phrase": [],
            },
            {
                "block": 15,
                "name": "WEIGHT",
                "search_phrase": ["WEIGHT", "GROSS WEIGHT", "NET WEIGHT", "PESO", "POIDS", "BRUTTO"],
                "minus_phrase": [],
            },
            {
                "block": 16,
                "name": "FRESH",
                "search_phrase": ["FRESH", "FRESCO"],
                "minus_phrase": [],
            },
            {
                "block": 17,
                "name": "FRUITS",
                "search_phrase": ["FRUIT", "FRUITS", "BANANA", "PLATANO", "PLÁTANO"],
                "minus_phrase": [],
            }
        ]
    },

    # Пример спецконфига для CHARTER (shipper-independent)
    "CHARTER": {
        "TITLE_0": [
            {
                "block": 0,
                "source": "title",
                "type": "format",
                "pattern": r'CODE NAME: "CONGENBILL". EDITION 1994',
                "var_name": "FORMAT",
                "target": "EXTRACT"
            }
        ],
        "TITLE_2": [
            {
                "block": 2,
                "source": "title",
                "type": "box",
                "pattern": r"BILL OF LADING B/L No\.?\s*([A-Z0-9]+)",
                "minus_phrase": ["BILL OF LADING B/L No."],
                "validation": r"^[A-Z0-9]+$",
                "var_name": "BILL_OF_LADING_NO",
                "target": "EXTRACT"
            }
        ],
        "TITLE_3": [
            {
                "block": 3,
                "source": "title",
                "type": "shipper",
                "pattern": r"Shipper\s*:?(.+)",
                "minus_phrase": ["Shipper"],
                "var_name": "SHIPPER",
                "target": "EXTRACT"
            }
        ],
        "TITLE_4": [
            {
                "block": 4,
                "source": "title",
                "type": "consignee",
                "pattern": r'Consignee\s*:?(.+)',
                "minus_phrase": ['Consignee'],
                "var_name": "CONSIGNEE",
                "target": "EXTRACT"
            }
        ],
        "TITLE_5": [
            {
                "block": 5,
                "source": "title",
                "type": "notify",
                "pattern": r"Notify\s*:?(.+)",
                "minus_phrase": ["Notify"],
                "var_name": "NOTIFY",
                "target": "EXTRACT"
            }
        ],
        "TITLE_6": [
            {
                "block": 6,
                "source": "title",
                "type": "vessel",
                "pattern": r"Vessel\s*:?(.+)",
                "minus_phrase": ["Vessel"],
                "var_name": "VESSEL",
                "target": "EXTRACT"
            }
        ],
        "TITLE_7": [
            {
                "block": 7,
                "source": "title",
                "type": "port_loading",
                "pattern": r"Port of Loading\s*:?(.+)",
                "minus_phrase": ["Port of Loading"],
                "var_name": "PORT_OF_LOADING",
                "target": "EXTRACT"
            }
        ],
        "TITLE_8": [
            {
                "block": 8,
                "source": "title",
                "type": "port_discharge",
                "pattern": r"Port of Discharge\s*:?(.+)",
                "minus_phrase": ["Port of Discharge"],
                "var_name": "PORT_OF_DISCHARGE",
                "target": "EXTRACT"
            }
        ],
        "TITLE_10": [
            {
                "block": 10,
                "source": "title",
                "type": "place_date_issue",
                "pattern": r"Place and date of issue\s*:?(.+)",
                "minus_phrase": ["Place and date of issue"],
                "var_name": "PLACE_AND_DATE_OF_ISSUE",
                "target": "EXTRACT"
            }
        ],
        "RIDER_12": [
            {
                "block": 12,
                "source": "rider",
                "type": "cont",
                "pattern": r"\b([A-Z]{4}\d{7})\b",
                "validation": r"^[A-Z]{4}\d{7}$",
                "var_name": "container",
            }
        ],
        "RIDER_13": [
            {
                "block": 13,
                "source": "rider",
                "type": "fresh",
                "pattern": r"\bFRESH\b",
                "validation": r"^FRESH$",
                "var_name": "fresh",
            },
            {
                "block": 13,
                "source": "rider",
                "type": "fruits",
                "pattern": r"\b(" + "|".join(FRUITS) + r")\b",
                "validation": r"^(" + "|".join(FRUITS) + r")$",
                "var_name": "fruits",
            },
            {
                "block": 13,
                "source": "rider",
                "type": "per_box",
                "pattern": r"\b(\d{2}[,.]\d{2})\b",
                "validation": r"^\d{2}[,.]\d{2}$",
                "var_name": "per_box",
            }
        ],
        "RIDER_14": [
            {
                "block": 14,
                "source": "rider",
                "type": "weight",
                "pattern": r'(\d{1,3}(?:,\d{3})*\.\d{2})\s*KGS',
                "var_name": "EX14_total_GCW",
            }
        ],
        "RIDER_15": [
            {
                "block": 15,
                "source": "rider",
                "type": "box",
                "pattern": r"(\d{1,5})",
                "validation": r"^\d{1,5}$",
                "var_name": "box_qty"
            }
        ]
    }
}




# Дополнительно: поддержка определения shipper по частичному совпадению
SHIPPER_KEYWORDS = [
    "EXPORTADORA DE BANANO",
    "GREEN EXPRESS",
    "FRIENDLY ORGANIC",
    "ECUAGREENPRODEX",
    "REYBANPAC",
    "BAGATOCORP",
    "HACIENDA GUAYABO GUAYABOSA"
]

def detect_shipper(text):
    """
    Находит шиппера по частичному совпадению текста
    :param text: str (SHIPPER block value)
    :return: str or None
    """
    for keyword in SHIPPER_KEYWORDS:
        if keyword.lower() in text.lower():
            return keyword
    return None

