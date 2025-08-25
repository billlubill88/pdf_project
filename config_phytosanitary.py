import re

PHYTOSANITARY_CONFIG = {
    "ECUADOR": {
        "page1_vertical": [
##            {"num": 100, "name": "Country", "left_pct": 0, "top_pct": 0, "right_pct": 29.21, "bottom_pct": 10},
##            {"num": 101, "name": "Agencia", "left_pct": 50, "top_pct": 0, "right_pct": 100, "bottom_pct": 8.5},
##            {"num": 102, "name": "PHYTOSANITARY CERTIFICATE", "left_pct": 29.5, "top_pct": 8.27, "right_pct": 70.79, "bottom_pct": 13.15},
            {"num": 103, "name": "№ Фитки", "left_pct": 8.87, "top_pct": 11, "right_pct": 30.27, "bottom_pct": 13.15},
            {"num": 1, "name": "1. Name and address of exporter", "left_pct": 3.91, "top_pct": 23.91, "right_pct": 50.03, "bottom_pct": 27.41},
            {"num": 2, "name": "2. Declared name and address of consignee", "left_pct": 50.11, "top_pct": 23.91, "right_pct": 96.23, "bottom_pct": 27.41},
            {"num": 3, "name": "3. Place of origin", "left_pct": 3.91, "top_pct": 29.25, "right_pct": 50.03, "bottom_pct": 32.16},
            {"num": 4, "name": "4. Declared means of conveyance", "left_pct": 50.11, "top_pct": 29.25, "right_pct": 96.23, "bottom_pct": 32.16},
            {"num": 5, "name": "5. Declared point of entry", "left_pct": 3.91, "top_pct": 34, "right_pct": 50.03, "bottom_pct": 38.1},
            {"num": 6, "name": "6. Distinguishing marks", "left_pct": 50.11, "top_pct": 34, "right_pct": 96.23, "bottom_pct": 38.1},
            {"num": 7, "name": "7. Number and description of packages", "left_pct": 3.91, "top_pct": 41.13, "right_pct": 50.03, "bottom_pct": 45.82},
            {"num": 8, "name": "8. Name of product and quantity declared", "left_pct": 50.11, "top_pct": 41.13, "right_pct": 96.23, "bottom_pct": 45.82},
            {"num": 9, "name": "9. Botanical name of plants", "left_pct": 3.91, "top_pct": 47.67, "right_pct": 96.22, "bottom_pct": 49.98},
            {"num": 10, "name": "10. Date", "left_pct": 3.91, "top_pct": 66.55, "right_pct": 50.03, "bottom_pct": 70.07},
            {"num": 11, "name": "11. Treatment", "left_pct": 50.11, "top_pct": 66.55, "right_pct": 96.23, "bottom_pct": 70.06},
            {"num": 12, "name": "12. Chemical (active ingredient)", "left_pct": 3.91, "top_pct": 73.08, "right_pct": 50.03, "bottom_pct": 76.6},
            {"num": 13, "name": "13. Duration and temperature", "left_pct": 50.11, "top_pct": 73.09, "right_pct": 73.04, "bottom_pct": 76.59},
            {"num": 14, "name": "14. Concentration", "left_pct": 73.13, "top_pct": 73.09, "right_pct": 96.22, "bottom_pct": 76.59},
            {"num": 15, "name": "15. Additional information", "left_pct": 3.91, "top_pct": 78.43, "right_pct": 96.22, "bottom_pct": 85.26},
            {"num": 16, "name": "Place of issue", "left_pct": 20.2, "top_pct": 85.32, "right_pct": 46.67, "bottom_pct": 88.23},
            {"num": 17, "name": "Date", "left_pct": 20.2, "top_pct": 88.29, "right_pct": 46.67, "bottom_pct": 90.01},
            {"num": 18, "name": "Name of Authorized Officer", "left_pct": 3.91, "top_pct": 91.86, "right_pct": 46.67, "bottom_pct": 93.58}
        ],
        "page2_horizontal": [
##            {"num": 100, "name": "Country", "left_pct": 0, "top_pct": 0, "right_pct": 22.16, "bottom_pct": 15},
##            {"num": 101, "name": "Agencia", "left_pct": 62.4, "top_pct": 0, "right_pct": 100, "bottom_pct": 13.76},
##            {"num": 102, "name": "PHYTOSANITARY CERTIFICATE", "left_pct": 30.12, "top_pct": 12.1, "right_pct": 69.74, "bottom_pct": 22.14},
            {"num": 103, "name": "№ Фитки", "left_pct": 8.64, "top_pct": 17.06, "right_pct": 32.39, "bottom_pct": 22.14},
            {"num": 4, "name": "Product", "left_pct": 2.4, "top_pct": 34.83, "right_pct": 23.72, "bottom_pct": 37.42},
            {"num": 5, "name": "Quantity", "left_pct": 23.79, "top_pct": 34.83, "right_pct": 33.24, "bottom_pct": 37.42},
            {"num": 6, "name": "Net Weight", "left_pct": 33.29, "top_pct": 34.83, "right_pct": 42.74, "bottom_pct": 37.42},
            {"num": 7, "name": "Gross Weight", "left_pct": 42.79, "top_pct": 34.83, "right_pct": 52.24, "bottom_pct": 37.42},
            {"num": 8, "name": "Treatment", "left_pct": 52.29, "top_pct": 34.83, "right_pct": 61.74, "bottom_pct": 37.42},
            {"num": 9, "name": "Dur. Temperatura", "left_pct": 61.8, "top_pct": 34.83, "right_pct": 71.25, "bottom_pct": 37.42},
            {"num": 10, "name": "Concentration", "left_pct": 71.3, "top_pct": 34.83, "right_pct": 80.75, "bottom_pct": 37.42},
            {"num": 11, "name": "Chemical", "left_pct": 80.8, "top_pct": 34.83, "right_pct": 90.25, "bottom_pct": 37.42},
            {"num": 12, "name": "Date", "left_pct": 90.31, "top_pct": 34.83, "right_pct": 97.38, "bottom_pct": 37.42},
            {"num": 13, "name": "Product", "left_pct": 2.4, "top_pct": 41.71, "right_pct": 23.72, "bottom_pct": 52.21},
            {"num": 14, "name": "Additional Declaration", "left_pct": 23.79, "top_pct": 41.71, "right_pct": 97.5, "bottom_pct": 52.21},
            {"num": 15, "name": "Adicional Information", "left_pct": 2.4, "top_pct": 57.34, "right_pct": 97.49, "bottom_pct": 62.8},
            {"num": 16, "name": "Place of issue", "left_pct": 23.79, "top_pct": 83.71, "right_pct": 45.11, "bottom_pct": 86.14},
            {"num": 17, "name": "Date", "left_pct": 23.79, "top_pct": 86.24, "right_pct": 45.11, "bottom_pct": 88.67},
            {"num": 18, "name": "Name of Authorized Officer", "left_pct": 2.4, "top_pct": 91.28, "right_pct": 45.11, "bottom_pct": 93.71}
        ]
    }
}

PHYTO_CONTAINER_PATTERN = r'\b([A-Z]{4}\d{7})\b'

PHYTO_VALIDATION_PATTERNS = {
    'means_of_conveyance': re.compile(r'Maritime', re.IGNORECASE),
    'na_check': re.compile(r'^N/A$', re.IGNORECASE)
}
