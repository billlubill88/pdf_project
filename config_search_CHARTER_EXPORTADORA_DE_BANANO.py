import re
from configs.config_fruits import FRUITS, FRUIT_TRANSLATIONS

SEARCH_CONFIG = {
    "CHARTER": {
        # TITLE-блоки: стандартные извлечения
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

        # RIDER 12: извлекаем только номера контейнеров и итоговые данные (после черты)
        "RIDER_12": [
            {
                "block": 12,
                "source": "rider",
                "type": "cont",
                "pattern": r"\b([A-Z]{4}\d{7})\b",
                "validation": r"^[A-Z]{4}\d{7}$",
                "var_name": "container",
            },
            # Итоговая строка в самом конце: BRAND: ... 4800 BOXES TYPE 22XU
            {
                "block": 12,
                "source": "rider",
                "type": "box",
                "pattern": r"(\d{2,5})\s*BOXES",
                "validation": r"^\d{2,5}$",
                "var_name": "EX_12_total_boxes",
                "target": "EXTRACT"
            },
            {
                "block": 12,
                "source": "rider",
                "type": "type_code",
                "pattern": r"TYPE\s*([A-Z0-9]{3,})",
                "validation": r"^[A-Z0-9]{3,}$",
                "var_name": "EX_12_type_code",
                "target": "EXTRACT"
            }
        ],

        # RIDER 13: извлекаем итоговые значения из финальной части блока!
        "RIDER_13": [
            # Итоговая конструкция: BOX(ES) of CONTAINING ... TYPE 22XU ... OF 20.80 GROSS WEIGHT PER BOX ...
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
            # Вытаскиваем variety, type, quality при необходимости — если нужно, добавь сюда.
            # Вытаскиваем веса для одного контейнера (GROSS/NET WEIGHT : ...)
            {
                "block": 13,
                "source": "rider",
                "type": "weight_one_cont",
                "pattern": r"GROSS WEIGHT\s*:\s*([\d,\.]+)\s*KGS",
                "var_name": "EX_13_GW_one_cont"
            },
            {
                "block": 13,
                "source": "rider",
                "type": "net_weight_one_cont",
                "pattern": r"NET WEIGHT\s*:\s*([\d,\.]+)\s*KGS",
                "var_name": "EX_13_NW_one_cont"
            },
            # Общий вес (тотал), он идёт после первой пары (GROSS/NET) — ищем второе вхождение
            {
                "block": 13,
                "source": "rider",
                "type": "weight_total",
                "pattern": r"GROSS WEIGHT\s*:\s*([\d,\.]+)\s*KGS",
                "var_name": "EX13_total_GW",
                "find_second": True
            },
            {
                "block": 13,
                "source": "rider",
                "type": "net_weight_total",
                "pattern": r"NET WEIGHT\s*:\s*([\d,\.]+)\s*KGS",
                "var_name": "EX13_total_NW",
                "find_second": True
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
