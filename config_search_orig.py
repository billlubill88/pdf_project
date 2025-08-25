import re

# Обновленный кортеж FRUITS с английскими названиями
FRUITS = (
    'BANANAS', 'APPLES', 'ORANGES', 'GRAPES', 
    'BLUEBERRIES', 'AVOCADO', 'PEARS'
)

# Словарь переводов фруктов
FRUIT_TRANSLATIONS = {
    'BANANAS': {'es': 'banano', 'la': 'Musa sapientum'},
    'APPLES': {'es': 'manzana', 'la': 'Malus domestica'},
    'ORANGES': {'es': 'naranja', 'la': 'Citrus × sinensis'},
    'GRAPES': {'es': 'uva', 'la': 'Vitis vinifera'},
    'BLUEBERRIES': {'es': 'arándano', 'la': 'Vaccinium corymbosum'},
    'AVOCADO': {'es': 'aguacate', 'la': 'Persea americana'},
    'PEARS': {'es': 'pera', 'la': 'Pyrus communis'}
}

SEARCH_LIST = [
    {
        'name': 'container',
        'type': 'cont',
        'blocks': [12],
        'pattern': {'all': r'\b([A-Z]{4}\d{7})\b'},
        'validation': r'^[A-Z]{4}\d{7}$',
        'source': 'RIDER',
        'format_type': ['all'],
        'target': 'CONTAINERS'
    },
    {
        'name': 'box_qty',
        'type': 'box',
        'blocks': [13],
        'pattern': {
            'CURSIV': r'\b(\d+)\s*BOXES?\b',
            'GOST-Multi': r'(\d+)\s*BOX\(ES\)',
            'DOSYL': r'(\d+)\s*CTNS?',
            'all': r'(\d+)\s*BOX\(ES\)'
        },
        'validation': r'^\d+$',
        'source': 'RIDER',
        'format_type': ['GOST-Multi', 'GOST-Mono'],
        'target': 'CONTAINERS',
        'flags': re.IGNORECASE
    },
    {
        'name': 'gross_weight',
        'type': 'weight',
        'blocks': [14],
        'pattern': {
            'CURSIV': r'(\d+\.\d{3})\s*(?:KGS|kgs|kg)',
            'all': r'(\d{1,3}(?:,\d{3})*\.\d{3})\s*(?:KGS|kgs|kg)'
        },
        'source': 'RIDER',
        'format_type': ['all'],
        'target': 'CONTAINERS',
        'post_process': lambda m: m.replace('.', ','),
        'final_var': 'EX14_total_GCW',
        # Убираем фильтрацию последнего значения на уровне обработки блоков
    },
    {
        'name': 'EX13_qty_CONT',
        'type': 'quantity',
        'blocks': [13],
        'pattern': {
            'GOST-Multi': r'(\d{1,3})\s*[xX]+\s*\d{2}[\'\"]',
            'DOSYL': r'(\d+)\s*CTNS?',
            'CURSIV': r'(\d{1,3})\s*[xX]+\s*\d{2}[\'\"]'
        },
        'validation': r'^\d+$',
        'source': 'RIDER',
        'format_type': ['GOST-Multi', 'GOST-Mono'],
        'target': 'EXTRACT',
        'var_name': 'EX13_qty_CONT'
    },
    {
        'name': 'carriers_receipt',
        'type': 'carriers_receipt',
        'blocks': [9],
        'pattern': {'all': r'\b(\d{1,3})\b'},
        'validation': r'^\d+$',
        'source': 'TITLE',
        'format_type': ['GOST-Multi', 'GOST-Mono'],
        'target': 'EXTRACT',
        'var_name': 'EX9_qty_CONT_CARRIERS'
    },
    {
        'name': 'PER_BOX',
        'type': 'per_box',
        'blocks': [13],
        'pattern': {
            'GOST-Mono': r'\b(\d{2}[,.]\d{2})\b',
            'GOST-Multi': r'\b(\d{2}[,.]\d{2})\b'
        },
        'validation': r'^\d{2}[,.]\d{2}$',
        'source': 'RIDER',
        'format_type': ['GOST-Mono', 'GOST-Multi'],
        'target': 'CONTAINERS',
        'var_name': 'perbox',
        'post_process': lambda values: per_box_post_process(values)
    },
    {
        'name': 'EX13_total_items',
        'type': 'total_items',
        'blocks': [13],
        'pattern': {
            'all': r'Total\s*Items\s*:\s*(\d+)'
        },
        'validation': r'^\d+$',
        'source': 'RIDER',
        'format_type': ['all'],
        'target': 'EXTRACT',
        'var_name': 'EX13_total_items'
    },
    {
    'name': 'fresh',
    'type': 'fresh',
    'blocks': [13],
    'pattern': {'all': r'\bFRESH\b'},
    'validation': r'^FRESH$',
    'source': 'RIDER',
    'format_type': ['all'],
    'target': 'CONTAINERS',
    'data_type': 'string'  # Новая опция
    },
    {
    'name': 'fruits',
    'type': 'fruits',
    'blocks': [13],
    'pattern': {'all': r'\b(' + '|'.join(FRUITS) + r')\b'},
    'validation': r'^(' + '|'.join(FRUITS) + r')$',
    'source': 'RIDER',
    'format_type': ['all'],
    'target': 'CONTAINERS',
    'data_type': 'string' # Новая опция
    }
]

PHYTO_CONTAINER_PATTERN = r'\b([A-Z]{4}\d{7})\b'
PHYTO_VALIDATION_PATTERNS = {
    'means_of_conveyance': re.compile(r'Maritime', re.IGNORECASE),
    'na_check': re.compile(r'^N/A$', re.IGNORECASE)
}

