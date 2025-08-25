BASE_BLOCKS = [
    {
        "num": 0,
        "left_pct": 0,
        "top_pct": 94.14,
        "right_pct": 100,
        "bottom_pct": 100,
        "page": 1,
        "name": "Standard Edition",
        "pattern": r'^Standard Edition - (01/2017|02/2015)\b'
    }
]

BLOCKS_CONFIG = {
    "GOST-Mono": {
        "title_blocks": [
            {"num": 1, "left_pct": 11.16, "top_pct": 3.25, "right_pct": 44.39, "bottom_pct": 4.36, "page": 1, "name": "SHIPPING COMPANY (1)", "pattern": r'MEDITERRANEAN SHIPPING COMPANY S.A.'},
            {"num": 2, "left_pct": 77.01, "top_pct": 2.94, "right_pct": 90.4, "bottom_pct": 4.16, "page": 1, "name": "BILL OF LADING No. (1)"},
            {"num": 3, "left_pct": 3.38, "top_pct": 9.64, "right_pct": 50.81, "bottom_pct": 14.6, "page": 1, "name": "SHIPPER (1)"},
            {"num": 4, "left_pct": 3.38, "top_pct": 15.63, "right_pct": 50.81, "bottom_pct": 20.89, "page": 1, "name": "CONSIGNEE (1)"},
            {"num": 5, "left_pct": 3.38, "top_pct": 22.94, "right_pct": 50.81, "bottom_pct": 28.39, "page": 1, "name": "NOTIFY PARTIES (1)"},
            {"num": 6, "left_pct": 3.38, "top_pct": 29.79, "right_pct": 35.4, "bottom_pct": 31.14, "page": 1, "name": "VESSEL AND VOYAGE NO (1)"},
            {"num": 7, "left_pct": 35.47, "top_pct": 29.79, "right_pct": 61.27, "bottom_pct": 31.14, "page": 1, "name": "PORT OF LOADING (1)"},
            {"num": 8, "left_pct": 35.47, "top_pct": 32.84, "right_pct": 61.27, "bottom_pct": 34.46, "page": 1, "name": "PORT DISCHARGE (1)"},
            {"num": 9, "left_pct": 31.85, "top_pct": 89.51, "right_pct": 59.74, "bottom_pct": 90.99, "page": 1, "name": "CARRIER'S RECEIPT (1)", "pattern": r'\b\d{1,3}\b'},
            {"num": 10, "left_pct": 17.51, "top_pct": 91.05, "right_pct": 31.78, "bottom_pct": 94.08, "page": 1, "name": "PLACE AND DATE OF ISSUE (1)", "pattern": r'\d{2}-[A-Z][a-z]{2}-\d{4}'},
            {"num": 11, "left_pct": 31.85, "top_pct": 92.25, "right_pct": 45.79, "bottom_pct": 94.09, "page": 1, "name": "SHIPPED ON BOARD DATE (1)", "pattern": r'\d{2}-[A-Z][a-z]{2}-\d{4}'}
        ],
        "rider_blocks": [
            {"num": 12, "left_pct": 3.32, "top_pct": 38.43, "right_pct": 23.03, "bottom_pct": 68.11, "page": 1, "name": "Container Numbers (1)"},
            {"num": 13, "left_pct": 23.11, "top_pct": 38.43, "right_pct": 78.71, "bottom_pct": 68.43, "page": 1, "name": "Description of Goods (1)"},
            {"num": 14, "left_pct": 78.8, "top_pct": 38.43, "right_pct": 87.53, "bottom_pct": 68.43, "page": 1, "name": "Gross Weight (1)"}
        ],
        "dynamic_rider": {
            12: {"left_pct": 3.85, "top_pct": 13.82, "right_pct": 23.29, "bottom_pct": 87.91, "name": "Container Numbers"},
            13: {"left_pct": 23.38, "top_pct": 13.82, "right_pct": 74.22, "bottom_pct": 88.33, "name": "Description of Goods"},
            14: {"left_pct": 74.3, "top_pct": 13.82, "right_pct": 85.31, "bottom_pct": 88.33, "name": "Gross Weight"}
        }
    },
    "GOST-Multi": {
        "title_blocks": [
            {"num": 1, "left_pct": 11.16, "top_pct": 3.25, "right_pct": 44.39, "bottom_pct": 4.36, "page": 1, "name": "SHIPPING COMPANY (1)", "pattern": r'MEDITERRANEAN SHIPPING COMPANY S.A.'},
            {"num": 2, "left_pct": 77.01, "top_pct": 2.94, "right_pct": 90.4, "bottom_pct": 4.16, "page": 1, "name": "BILL OF LADING No. (1)"},
            {"num": 3, "left_pct": 3.38, "top_pct": 9.64, "right_pct": 50.81, "bottom_pct": 14.6, "page": 1, "name": "SHIPPER (1)"},
            {"num": 4, "left_pct": 3.38, "top_pct": 15.63, "right_pct": 50.81, "bottom_pct": 20.89, "page": 1, "name": "CONSIGNEE (1)"},
            {"num": 5, "left_pct": 3.38, "top_pct": 22.94, "right_pct": 50.81, "bottom_pct": 28.39, "page": 1, "name": "NOTIFY PARTIES (1)"},
            {"num": 6, "left_pct": 3.38, "top_pct": 29.79, "right_pct": 35.4, "bottom_pct": 31.14, "page": 1, "name": "VESSEL AND VOYAGE NO (1)"},
            {"num": 7, "left_pct": 35.47, "top_pct": 29.79, "right_pct": 61.27, "bottom_pct": 31.14, "page": 1, "name": "PORT OF LOADING (1)"},
            {"num": 8, "left_pct": 35.47, "top_pct": 32.84, "right_pct": 61.27, "bottom_pct": 34.46, "page": 1, "name": "PORT DISCHARGE (1)"},
            {"num": 9, "left_pct": 31.85, "top_pct": 89.51, "right_pct": 59.74, "bottom_pct": 90.99, "page": 1, "name": "CARRIER'S RECEIPT (1)", "pattern": r'\b\d{1,3}\b'},
            {"num": 10, "left_pct": 17.51, "top_pct": 91.05, "right_pct": 31.78, "bottom_pct": 94.08, "page": 1, "name": "PLACE AND DATE OF ISSUE (1)", "pattern": r'\d{2}-[A-Z][a-z]{2}-\d{4}'},
            {"num": 11, "left_pct": 31.85, "top_pct": 92.25, "right_pct": 45.79, "bottom_pct": 94.09, "page": 1, "name": "SHIPPED ON BOARD DATE (1)", "pattern": r'\d{2}-[A-Z][a-z]{2}-\d{4}'}
        ],
        "rider_blocks": [
            {"num": 13, "left_pct": 23.11, "top_pct": 38.43, "right_pct": 78.71, "bottom_pct": 68.43, "page": 1, "name": "Description of Goods (1)"},
        ],
        "dynamic_rider": {
            12: {"left_pct": 3.85, "top_pct": 13.82, "right_pct": 23.29, "bottom_pct": 87.91, "name": "Container Numbers"},
            13: {"left_pct": 23.38, "top_pct": 13.82, "right_pct": 74.22, "bottom_pct": 88.33, "name": "Description of Goods"},
            14: {"left_pct": 74.3, "top_pct": 13.82, "right_pct": 85.31, "bottom_pct": 88.33, "name": "Gross Weight"}
        }
    },
    "DOSYL": {
        "title_blocks": [
            {"num": 1, "left_pct": 11.29, "top_pct": 2.77, "right_pct": 48.78, "bottom_pct": 5.89, "page": 1, "name": "SHIPPING COMPANY (1)", "pattern": r'MEDITERRANEAN SHIPPING COMPANY S.A.'},
            {"num": 2, "left_pct": 77.61, "top_pct": 2.77, "right_pct": 96.53, "bottom_pct": 5.89, "page": 1, "name": "BILL OF LADING No. (1)"},
            {"num": 3, "left_pct": 3.91, "top_pct": 11.73, "right_pct": 48.78, "bottom_pct": 17.55, "page": 1, "name": "SHIPPER (1)"},
            {"num": 4, "left_pct": 3.91, "top_pct": 19.65, "right_pct": 48.78, "bottom_pct": 25.44, "page": 1, "name": "CONSIGNEE (1)"},
            {"num": 5, "left_pct": 3.91, "top_pct": 28.52, "right_pct": 48.78, "bottom_pct": 34.33, "page": 1, "name": "NOTIFY PARTIES (1)"},
            {"num": 6, "left_pct": 3.91, "top_pct": 35.98, "right_pct": 32.59, "bottom_pct": 37.57, "page": 1, "name": "VESSEL AND VOYAGE NO (1)"},
            {"num": 7, "left_pct": 32.72, "top_pct": 35.98, "right_pct": 62.41, "bottom_pct": 37.57, "page": 1, "name": "PORT OF LOADING (1)"},
            {"num": 8, "left_pct": 32.72, "top_pct": 39.06, "right_pct": 62.41, "bottom_pct": 40.65, "page": 1, "name": "PORT DISCHARGE (1)"},
            {"num": 9, "left_pct": 1.000, "top_pct": 1.000, "right_pct": 2.000, "bottom_pct": 2.000, "page": 1, "name": "CARRIER'S RECEIPT (1)", "pattern": r'\b\d{1,3}\b'},
            {"num": 10, "left_pct": 3.91, "top_pct": 86.95, "right_pct": 17.55, "bottom_pct": 88.38, "page": 1, "name": "PLACE AND DATE OF ISSUE (1)", "pattern": r'\d{2}-[A-Z][a-z]{2}-\d{4}'},
            {"num": 11, "left_pct": 17.54, "top_pct": 86.95, "right_pct": 31.18, "bottom_pct": 88.38, "page": 1, "name": "SHIPPED ON BOARD DATE (1)", "pattern": r'\d{2}-[A-Z][a-z]{2}-\d{4}'}
        ],
        "rider_blocks": [
            {"num": 12, "left_pct": 4.05, "top_pct": 44.69, "right_pct": 23.67, "bottom_pct": 63.38, "page": 1, "name": "Container Numbers (1)"},
            {"num": 13, "left_pct": 23.79, "top_pct": 44.69, "right_pct": 73.88, "bottom_pct": 63.38, "page": 1, "name": "Description of Goods (1)"},
            {"num": 14, "left_pct": 73.96, "top_pct": 44.69, "right_pct": 83.9, "bottom_pct": 63.38, "page": 1, "name": "Gross Weight (1)"}
        ],
        "dynamic_rider": {
            12: {"left_pct": 3.82, "top_pct": 17.81, "right_pct": 23.28, "bottom_pct": 86.82},
            13: {"left_pct": 23.4, "top_pct": 17.81, "right_pct": 72.69, "bottom_pct": 86.82},
            14: {"left_pct": 72.8, "top_pct": 17.81, "right_pct": 82.62, "bottom_pct": 86.82}
        }
    },
    "CURSIV": {
        "title_blocks": [
            {"num": 1, "left_pct": 10.35, "top_pct": 3.69, "right_pct": 49.79, "bottom_pct": 6.27, "page": 1, "name": "SHIPPING COMPANY (1)", "pattern": r'MEDITERRANEAN SHIPPING COMPANY S.A.'},
            {"num": 2, "left_pct": 72.35, "top_pct": 3.7, "right_pct": 95.13, "bottom_pct": 5.47, "page": 1, "name": "BILL OF LADING No. (1)"},
            {"num": 3, "left_pct": 3.85, "top_pct": 10.65, "right_pct": 49.81, "bottom_pct": 15.91, "page": 1, "name": "SHIPPER (1)"},
            {"num": 4, "left_pct": 3.85, "top_pct": 17.03, "right_pct": 49.81, "bottom_pct": 22.37, "page": 1, "name": "CONSIGNEE (1)"},
            {"num": 5, "left_pct": 3.85, "top_pct": 24.39, "right_pct": 49.81, "bottom_pct": 30.72, "page": 1, "name": "NOTIFY PARTIES (1)"},
            {"num": 6, "left_pct": 3.85, "top_pct": 32.05, "right_pct": 34.36, "bottom_pct": 34.1, "page": 1, "name": "VESSEL AND VOYAGE NO (1)"},
            {"num": 7, "left_pct": 34.44, "top_pct": 32.04, "right_pct": 60.4, "bottom_pct": 34.09, "page": 1, "name": "PORT OF LOADING (1)"},
            {"num": 8, "left_pct": 34.44, "top_pct": 35.26, "right_pct": 60.4, "bottom_pct": 37.52, "page": 1, "name": "PORT DISCHARGE (1)"},
            {"num": 9, "left_pct": 31.46, "top_pct": 91.23, "right_pct": 59.02, "bottom_pct": 92.43, "page": 1, "name": "CARRIER'S RECEIPT (1)", "pattern": r'\b\d{1,3}\b'},
            {"num": 10, "left_pct": 3.85, "top_pct": 93.62, "right_pct": 31.39, "bottom_pct": 95.59, "page": 1, "name": "PLACE AND DATE OF ISSUE (1)", "pattern": r'\d{2}-[A-Z][a-z]{2}-\d{4}'},
            {"num": 11, "left_pct": 31.46, "top_pct": 93.62, "right_pct": 59.02, "bottom_pct": 96.34, "page": 1, "name": "SHIPPED ON BOARD DATE (1)", "pattern": r'\d{2}-[A-Z][a-z]{2}-\d{4}'}
        ],
        "rider_blocks": [
            {"num": 12, "left_pct": 3.89, "top_pct": 41.43, "right_pct": 22.27, "bottom_pct": 70.31, "page": 1, "name": "Container Numbers (1)"},
            {"num": 13, "left_pct": 22.35, "top_pct": 41.43, "right_pct": 76.87, "bottom_pct": 70.87, "page": 1, "name": "Description of Goods (1)"},
            {"num": 14, "left_pct": 76.97, "top_pct": 41.43, "right_pct": 86.33, "bottom_pct": 70.87, "page": 1, "name": "Gross Weight (1)"}
        ],
        "dynamic_rider": {
            12: {"left_pct": 3.85, "top_pct": 13.82, "right_pct": 23.29, "bottom_pct": 87.91},
            13: {"left_pct": 23.38, "top_pct": 13.82, "right_pct": 74.22, "bottom_pct": 88.33},
            14: {"left_pct": 74.3, "top_pct": 13.82, "right_pct": 85.31, "bottom_pct": 88.33}
        }
    }
}
