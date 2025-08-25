import re

# Список всех фруктов (обнови при необходимости)
FRUITS = (
    'BANANAS', 'APPLES', 'ORANGES', 'GRAPES', 
    'BLUEBERRIES', 'AVOCADO', 'PEARS'
)

FRUIT_TRANSLATIONS = {
    'BANANAS': {'es': 'banano', 'la': 'Musa sapientum'},
    'APPLES': {'es': 'manzana', 'la': 'Malus domestica'},
    'ORANGES': {'es': 'naranja', 'la': 'Citrus × sinensis'},
    'GRAPES': {'es': 'uva', 'la': 'Vitis vinifera'},
    'BLUEBERRIES': {'es': 'arándano', 'la': 'Vaccinium corymbosum'},
    'AVOCADO': {'es': 'aguacate', 'la': 'Persea americana'},
    'PEARS': {'es': 'pera', 'la': 'Pyrus communis'}
}


SEARCH_CONFIG = {
    "all": {
        # Универсальный пример (пока пустой)
    },
    "GOST-Multi": {
        "TITLE_2": [
            {
                "block": 2,
                "source": "title",
                "type": "box",
                "pattern": r"BILL OF LADING No\.?\s*([A-Z0-9]+)",
                "minus_phrase": ["BILL OF LADING No."],
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
                "pattern": r"SHIPPER:?\s*(.+)",
                "minus_phrase": ["SHIPPER:"],
                "var_name": "SHIPPER",
                "target": "EXTRACT"
            }
        ],
        "TITLE_4": [
            {
                "block": 4,
                "source": "title",
                "type": "consignee",
                "pattern": r'CONSIGNEE:.*?here\.\s*(.+)',
                "minus_phrase": ['CONSIGNEE: This B/L is not negotiable unless marked "To Order" or "To Order of ..." here.'],
                "var_name": "CONSIGNEE",
                "target": "EXTRACT"
            }
        ],
        "TITLE_5": [
            {
                "block": 5,
                "source": "title",
                "type": "notify",
                "pattern": r"NOTIFY PARTIES\s*:?(.+)",
                "minus_phrase": ["NOTIFY PARTIES : (No responsibility shall attach to Carrier or to his Agent for failure to notify - see  Clause 20)"],
                "var_name": "NOTIFY",
                "target": "EXTRACT"
            }
        ],
        "TITLE_6": [
            {
                "block": 6,
                "source": "title",
                "type": "vessel",
                "pattern": r"VOYAGE NO.+?([A-Z0-9\.\- ]+)",
                "minus_phrase": ["VESSEL AND VOYAGE NO (see Clause 8 & 9)"],
                "var_name": "VESSEL",
                "target": "EXTRACT"
            }
        ],
        "TITLE_7": [
            {
                "block": 7,
                "source": "title",
                "type": "port_loading",
                "pattern": r"PORT OF LOADING\s*(.+)",
                "minus_phrase": ["PORT OF LOADING"],
                "var_name": "PORT_OF_LOADING",
                "target": "EXTRACT"
            }
        ],
        "TITLE_8": [
            {
                "block": 8,
                "source": "title",
                "type": "port_discharge",
                "pattern": r"PORT OF DISCHARGE\s*(.+)",
                "minus_phrase": ["PORT OF DISCHARGE"],
                "var_name": "PORT_OF_DISCHARGE",
                "target": "EXTRACT"
            }
        ],
        "TITLE_9": [
            {
                "block": 9,
                "source": "title",
                "type": "carriers_receipt",
                "pattern": r'\b(\d{1,3})\b',
                "validation": r'^\d+$',
                "minus_phrase": ["CARRIER'S RECEIPT (No. of Cntrs or Pkgs rcvd by Carrier - see Clause 14.1)"],
                "var_name": "EX9_qty_CONT_CARRIERS",
                "target": "EXTRACT"
            }
        ],
        "TITLE_10": [
            {
                "block": 10,
                "source": "title",
                "type": "PLACE AND DATE OF ISSUE",
                "pattern": "",
                "minus_phrase": ["PLACE AND DATE OF ISSUE"],
                "var_name": "PLACE AND DATE OF ISSUE",
                "target": "EXTRACT"
            }
        ],
        "TITLE_11": [
            {
                "block": 11,
                "source": "title",
                "type": "SHIPPED ON BOARD DATE",
                "pattern": "SHIPPED ON BOARD DATE",
                "minus_phrase": ["SHIPPED ON BOARD DATE"],
                "var_name": "EX_1_11_SOB_date",
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
                "type": "box",
                "pattern": r"(\d+)\s*BOX\(ES\)",
                "validation": r"^\d+$",
                "var_name": "box_qty",
            },
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
            },
            {
                "block": 13,
                "source": "rider",
                "type": "box",
                "pattern": r"Total\s*Items\s*:\s*(\d+)",
                "validation": r"^\d+$",
                "var_name": "EX13_total_items",
                "target": "EXTRACT"
            },
            {
                "block": 13,
                "source": "rider",
                "type": "box",
                "pattern": r"(\d{1,4})\s*[xX]+\s*\d{2}[\'\"]",
                "validation": r"^\d+$",
                "var_name": "EX13_qty_CONT",
                "target": "EXTRACT"
            }
        ],
        "RIDER_14": [
            {
                "block": 14,
                "source": "rider",
                "type": "weight",
                "pattern": r"(\d{1,3}(?:,\d{3})*\.\d{3})\s*(?:KGS|kgs|kg)",
                "validation": None,
                "var_name": "EX14_total_GCW",
            }
        ]
    },
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

