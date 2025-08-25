# modules/document_processor.py
import logging
import gc
import re
from typing import List, Dict, Any, Tuple, Optional
import pdfplumber

from configs.config_blocks import BLOCKS_CONFIG
from configs.config_phytosanitary import PHYTOSANITARY_CONFIG, PHYTO_CONTAINER_PATTERN
from core.ml_blocks_adapter import (
    extract_blocks_from_pdf_page,
    extract_ml_title_blocks,
    extract_ml_rider_blocks,
)

class DocumentProcessor:
    """
    Слой обработки конкретных документов:
    - парсинг коносамента (process_pdf)
    - парсинг фитосертификата (process_phytosanitary)
    - извлечение блоков, применение minus-phrases, визуализация
    - формирование промежуточных структур в data_processor
    """

    def __init__(self, pdf_processor):
        # держим ссылки на все зависимости через основной PDFProcessor
        self.pdf = pdf_processor
        self.USE_ML = pdf_processor.USE_ML

        # короткие алиасы
        self.de = pdf_processor.data_extractor
        self.dp = pdf_processor.data_processor
        self.v = pdf_processor.validator
        self.viz = pdf_processor.visualizer

    # -------------------- Bill of Lading --------------------

    def process_pdf(self, pdf_path: str):
        """
        Основной разбор коносамента (динамическая подгрузка SEARCH_CONFIG).
        """
        try:
            self.pdf.file_manager.clean_workspace()

            with pdfplumber.open(pdf_path) as pdf:
                # --- Extract block 0 from ML predictions ---
                pred_blocks = extract_blocks_from_pdf_page(pdf_path, page_num=0)
                block0_text = None
                for block in pred_blocks:
                    if block.get('num', None) == 0:
                        block0_text = block.get('value', '').strip()
                        break

                if block0_text is None:
                    block0_text = ""

                # Determine format by block 0 text and page count
                format_type = self.de.determine_format(block0_text, num_pages=len(pdf.pages))
                print("\n" + "="*50)
                print("[Block 0] Standard Edition Block")
                print(f"Text: {block0_text}")

                print("\n" + "="*50)
                print(f"BILL OF LADING FORMAT: {format_type}")

                print("\n" + "="*50)
                print("RECOGNIZED BLOCKS:")

                # --- Determine SHIPPER for dynamic SEARCH_CONFIG import ---
                shipper_value = ""
                shipper_candidates = [
                    "EXPORTADORA DE BANANO",
                    "GREEN EXPRESS",
                    "FRIENDLY ORGANIC",
                    "ECUAGREENPRODEX",
                    "REYBANPAC",
                    "BAGATOCORP",
                    "HACIENDA GUAYABO GUAYABOSA"
                ]

                # Extract shipper text
                raw_shipper = ""
                for block in pred_blocks:
                    block_name = str(block.get('name', '')).lower()
                    if "shipper" in block_name or "exporter" in block_name:
                        raw_shipper = block.get('value', '').strip()
                        break
                if not raw_shipper:
                    shipper_block = [b for b in pred_blocks if b.get('num') == 3]
                    if shipper_block:
                        raw_shipper = shipper_block[0].get('value', '').strip()

                # Normalize to single case and spaces
                normalized_shipper = raw_shipper.upper().replace("  ", " ").strip()
                matched_shipper = ""
                for candidate in shipper_candidates:
                    if candidate in normalized_shipper:
                        matched_shipper = candidate
                        break
                if not matched_shipper:
                    matched_shipper = "ALL"

                # Now load SEARCH_CONFIG by format and found shipper (or ALL)
                if format_type == "CHARTER":
                    SEARCH_CONFIG = self.dynamic_import_config(format_type, matched_shipper)
                else:
                    from configs import config_search
                    SEARCH_CONFIG = config_search.SEARCH_CONFIG

                for page_num, page in enumerate(pdf.pages, 1):
                    if page_num == 1:
                        # --- TITLE BLOCKS ---
                        if self.USE_ML:
                            pred_blocks = extract_blocks_from_pdf_page(pdf_path, page_num-1)
                            title_blocks = extract_ml_title_blocks(pred_blocks, page_num)
                            for block in title_blocks:
                                self.process_and_print_block(page, block, "TITLE", format_type, SEARCH_CONFIG)
                        else:
                            for block in BLOCKS_CONFIG.get(format_type, {}).get("title_blocks", []):
                                self.process_and_print_block(page, block, "TITLE", format_type, SEARCH_CONFIG)

                    # --- RIDER BLOCKS ---
                    if self.USE_ML:
                        pred_blocks = extract_blocks_from_pdf_page(pdf_path, page_num-1)
                        rider_blocks = extract_ml_rider_blocks(pred_blocks, page_num)
                        for block in rider_blocks:
                            self.process_and_print_block(page, block, "RIDER", format_type, SEARCH_CONFIG)
                    else:
                        rider_blocks = self.get_rider_blocks(format_type, page_num, len(pdf.pages))
                        for block in rider_blocks:
                            self.process_and_print_block(page, block, "RIDER", format_type, SEARCH_CONFIG)

                self.search_variables(format_type, SEARCH_CONFIG)

                self.dp.post_process_weights()

        except Exception as e:
            logging.error(f"PDF processing error: {str(e)}")
            print(f"!!! EXECUTION ERROR !!!\nError type: {type(e).__name__}\nMessage: {e}")
            raise

    def dynamic_import_config(self, format_type: str, shipper_text: str):
        """
        Dynamic SEARCH_CONFIG import by format and shipper.
        If key shipper found - loads custom SEARCH_CONFIG,
        otherwise - loads general one.
        """
        import importlib

        SHIPPER_KEYS = [
            "EXPORTADORA DE BANANO",
            "GREEN EXPRESS",
            "FRIENDLY ORGANIC",
            "ECUAGREENPRODEX",
            "REYBANPAC",
            "BAGATOCORP",
            "HACIENDA GUAYABO GUAYABOSA"
        ]
        module_base = "configs.config_search"

        matched_shipper = None
        shipper_text_upper = shipper_text.upper()
        for key in SHIPPER_KEYS:
            if key in shipper_text_upper:
                matched_shipper = key.replace(" ", "_")
                break

        if matched_shipper:
            config_module_name = f"{module_base}_{format_type.upper()}_{matched_shipper}"
            try:
                config_module = importlib.import_module(config_module_name)
                print(f"Loaded module: {config_module_name}")
                return config_module.SEARCH_CONFIG
            except ModuleNotFoundError as e:
                print(f"[WARN] Module not found {config_module_name}: {e}")

        try:
            config_module = importlib.import_module("configs.config_search")
            print(f"Loaded general module: configs.config_search")
            return config_module.SEARCH_CONFIG
        except Exception as e:
            print(f"[ERROR] Error importing general SEARCH_CONFIG: {e}")
            raise

    def process_charter_bill(self, page, format_type):
        blocks = {}
        template = self.pdf.CHARTER_BLOCKS.get(format_type, self.pdf.CHARTER_BLOCKS["GENERIC"])
        shipper_coords = self.de.find_block_by_text(page, template["key_phrases"]["shipper"])
        if shipper_coords:
            blocks["shipper"] = {
                "coords": shipper_coords,
                "text": self.de.get_text_objects(page, shipper_coords)
            }
        table_coords = self.de.detect_table(page, template["key_phrases"]["goods_table"])
        if table_coords:
            blocks["goods_table"] = {
                "coords": table_coords,
                "rows": self.extract_table_rows(page, table_coords) if hasattr(self, "extract_table_rows") else []
            }
        return blocks

    def process_and_print_block(self, page, config, block_type, format_type, search_config):
        """
        Обработка блока: координаты -> текст -> minus-phrases -> визуализация -> запись в data_conos
        """
        try:
            import re

            # 1. Coordinates
            x0 = page.width * config['left_pct'] / 100
            top = page.height * config['top_pct'] / 100
            x1 = page.width * config['right_pct'] / 100
            bottom = page.height * config['bottom_pct'] / 100
            coords = (x0, top, x1, bottom)

            # 2. Extract text
            text = page.crop(coords).extract_text() or ""
            cleaned_text = " ".join(text.split()).strip()

            # 3. minus-phrases
            minus_phrases = []
            for search_area in ['all', format_type]:
                section = search_config.get(search_area, {})
                for block_key, block_templates in section.items():
                    is_title = block_type == "TITLE" and block_key.lower().startswith("title")
                    is_rider = block_type == "RIDER" and block_key.lower().startswith("rider")
                    if not (is_title or is_rider):
                        continue
                    for template in block_templates:
                        if template.get("block") != config['num']:
                            continue
                        minus_cfg = template.get('minus_phrase')
                        if not minus_cfg:
                            continue
                        if isinstance(minus_cfg, dict):
                            if format_type in minus_cfg:
                                minus_phrases += minus_cfg[format_type]
                            if 'all' in minus_cfg:
                                minus_phrases += minus_cfg['all']
                        elif isinstance(minus_cfg, list):
                            minus_phrases += minus_cfg
                        else:
                            minus_phrases.append(str(minus_cfg))

            if minus_phrases:
                for phrase in minus_phrases:
                    cleaned_text = re.sub(re.escape(phrase), '', cleaned_text, flags=re.IGNORECASE)
                cleaned_text = " ".join(cleaned_text.split()).strip()

            # 5. Visualization
            img_path = self.viz.visualize_block(page, config, block_type)

            # 6. Print information
            print(f"\n[{block_type} Block {config['num']}] {config.get('name', '')}")
            print("-" * 60)
            print(f"Page: {config['page']}")
            print(f"Coordinates (x0, top, x1, bottom): {tuple(round(c, 1) for c in coords)}")
            print(f"Text:\n{cleaned_text}")
            print(f"Visualization saved: {img_path if img_path else 'Failed'}")

            # 7. Save to final dictionary
            key = (config['page'], config['num'])
            target_dict = self.dp.data_conos['title'] if block_type == "TITLE" else self.dp.data_conos['rider']
            target_dict[key] = {
                'name': config.get('name', ''),
                'value': cleaned_text,
                'page_type': block_type,
                'image_path': img_path,
                'coordinates': coords
            }

        except Exception as e:
            error_msg = f"Error processing block {config.get('num', '?')}: {str(e)}"
            logging.error(error_msg)
            print(f"⚠ {error_msg}")

    def get_rider_blocks(self, format_type, page_num, total_pages):
        """Получение списка rider-блоков для страницы"""
        try:
            config = BLOCKS_CONFIG.get(format_type, {})
            if format_type in ["GOST-Mono", "DOSYL"]:
                return config.get("rider_blocks", [])
            elif format_type in ["GOST-Multi", "CURSIV"]:
                if page_num == 1:
                    return config.get("rider_blocks", [])
                else:
                    return self.generate_dynamic_blocks(page_num)
            return []
        except Exception as e:
            logging.error(f"Error getting blocks: {str(e)}")
            return []

    def generate_dynamic_blocks(self, page_num):
        """Динамическая генерация rider-блоков для страниц >1"""
        blocks = []
        base_config = {
            12: {"name": "Container Numbers"},
            13: {"name": "Description of Goods"}, 
            14: {"name": "Gross Weight"}
        }
        coordinates = {
            2: {
                12: {"left_pct": 3.85, "top_pct": 13.82, "right_pct": 23.29, "bottom_pct": 87.91},
                13: {"left_pct": 23.38, "top_pct": 13.82, "right_pct": 74.22, "bottom_pct": 88.33},
                14: {"left_pct": 74.3, "top_pct": 13.82, "right_pct": 85.31, "bottom_pct": 88.33}
            },
            'default': {
                12: {"left_pct": 3.85, "top_pct": 11.98, "right_pct": 23.29, "bottom_pct": 87.91},
                13: {"left_pct": 23.38, "top_pct": 11.98, "right_pct": 74.22, "bottom_pct": 88.34},
                14: {"left_pct": 74.29, "top_pct": 11.98, "right_pct": 85.3, "bottom_pct": 88.34}
            }
        }
        page_coords = coordinates[2] if page_num == 2 else coordinates['default']
        for block_num in [12, 13, 14]:
            block_config = {
                "num": block_num,
                "page": page_num,
                **base_config[block_num],
                **page_coords[block_num]
            }
            block_config["name"] = f"{block_config['name']} ({page_num})"
            blocks.append(block_config)
        return blocks

    # -------------------- Phytosanitary --------------------

    def process_phytosanitary(self, pdf_path: str):
        """Разбор фитосертификата (сохранение контейнеров в extract_phito)"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                format_type = self.de.determine_phytosanitary_format(pdf)
                print(f"\n[PHYTOSANITARY CERTIFICATE]")
                print(f"Format: {format_type}")
                print(f"Page count: {len(pdf.pages)}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    orientation = "page1_vertical" if page.height > page.width else "page2_horizontal"
                    blocks = PHYTOSANITARY_CONFIG[format_type].get(orientation, [])
                    
                    print(f"\nPage {page_num} ({orientation}):")
                    print(f"Dimensions: {page.width:.1f}x{page.height:.1f} pt")
                    
                    for block in blocks:
                        try:
                            x0 = page.width * block['left_pct'] / 100
                            y0 = page.height * block['top_pct'] / 100
                            x1 = page.width * block['right_pct'] / 100
                            y1 = page.height * block['bottom_pct'] / 100
                            
                            if y1 < y0:
                                y0, y1 = y1, y0
                            
                            coords = (x0, y0, x1, y1)
                            text = page.crop(coords).extract_text() or ""
                            cleaned_text = " ".join(text.split()).strip()

                            # Block 17 date strings (save raw)
                            if block['num'] == 17:
                                raw_text = (page.crop(coords).extract_text() or "").strip()
                                if orientation == 'page1_vertical':
                                    self.dp.extract_phito['EX_1_17_Date_PHITO'] = raw_text
                                else:
                                    self.dp.extract_phito['EX_2_17_Date_PHITO'] = raw_text
                            
                            # Certificate number (block 103)
                            if block['num'] == 103:
                                if orientation == "page1_vertical" and not self.dp.extract_phito['page1_number']:
                                    self.dp.extract_phito['page1_number'] = cleaned_text
                                elif orientation == "page2_horizontal" and not self.dp.extract_phito['page2_number']:
                                    self.dp.extract_phito['page2_number'] = cleaned_text
                            
                            # BOX / Box and containers by orientation
                            if orientation == "page1_vertical":
                                if block['num'] == 7:
                                    match = re.search(r'(\d+)\s*Box', cleaned_text, re.IGNORECASE)
                                    if match and not self.dp.extract_phito['PH1_Box']:
                                        self.dp.extract_phito['PH1_Box'] = int(match.group(1))
                                if block['num'] == 15:
                                    match = re.search(r'(\d{1,3}(?:\.\d{3})*)\s*BOXES', cleaned_text, re.IGNORECASE)
                                    if match and not self.dp.extract_phito['PH1_BOXES']:
                                        self.dp.extract_phito['PH1_BOXES'] = int(match.group(1).replace('.', ''))
                                    containers = re.findall(PHYTO_CONTAINER_PATTERN, text or "")
                                    if containers:
                                        self.dp.extract_phito.setdefault('Containers_PH_1', []).extend(containers)
                                        self.dp.extract_phito['Containers_PH_1'] = list(dict.fromkeys(self.dp.extract_phito['Containers_PH_1']))
                            
                            if orientation == "page2_horizontal":
                                if block['num'] == 5:
                                    match = re.search(r'(\d+)\s*Box', cleaned_text, re.IGNORECASE)
                                    if match and not self.dp.extract_phito['PH2_Box']:
                                        self.dp.extract_phito['PH2_Box'] = int(match.group(1))
                                if block['num'] == 15:
                                    match = re.search(r'(\d{1,3}(?:\.\d{3})*)\s*BOXES', cleaned_text, re.IGNORECASE)
                                    if match and not self.dp.extract_phito['PH2_BOXES']:
                                        self.dp.extract_phito['PH2_BOXES'] = int(match.group(1).replace('.', ''))
                                    containers = re.findall(PHYTO_CONTAINER_PATTERN, text or "")
                                    if containers:
                                        self.dp.extract_phito.setdefault('Containers_PH_2', []).extend(containers)
                                        self.dp.extract_phito['Containers_PH_2'] = list(dict.fromkeys(self.dp.extract_phito['Containers_PH_2']))
                            
                            # Visualization
                            img_path = self.viz.visualize_phytosanitary_block(page, block, orientation, page_num)
                            
                            # Save block data
                            key = (orientation, block['num'])
                            self.dp.data_phito[key] = {
                                'name': block['name'],
                                'value': cleaned_text,
                                'page_num': page_num,
                                'coordinates': coords,
                                'image_path': img_path
                            }
                            
                        except Exception as e:
                            logging.error(f"Error processing block {block.get('num', '?')}: {str(e)}")
                            continue
                
                # Update container counters
                self.dp.rows_count['phito']['total_cont_PH1'] = len(self.dp.extract_phito.get('Containers_PH_1', []))
                self.dp.rows_count['phito']['total_cont_PH2'] = len(self.dp.extract_phito.get('Containers_PH_2', []))
                
                # Output results
                print("\nProcessing complete:")
                print(f"Page 1 Containers: {self.dp.extract_phito.get('Containers_PH_1', [])}")
                print(f"Page 2 Containers: {self.dp.extract_phito.get('Containers_PH_2', [])}")
                print(f"Numbers: {self.dp.extract_phito['page1_number']} | {self.dp.extract_phito['page2_number']}")
                del page
                del pdf
                gc.collect()
        except Exception as e:
            logging.error(f"Error processing file {pdf_path}: {str(e)}")
            raise

    # -------------------- Search variables (B/L) --------------------

    def search_variables(self, format_type, SEARCH_CONFIG, shipper=None):
        """
        Search and extract variables from bill of lading.
        Supports minus-phrases, flexible patterns by format and shipper.
        """
        print("\n--- [LOG] Start search_variables ---")
        # Reset counters and data
        self.dp.rows_count['conos'] = {k: 0 for k in self.dp.rows_count['conos']}
        self.dp.extract_conos.update({k: 'N/A' if k.startswith('EX') else 0 for k in self.dp.extract_conos if k.startswith('EX') or k in ['total_fresh', 'total_fruits']})
        self.dp.extract_conos.update({k: [] for k in ['containers', 'boxes', 'weights', 'perbox', 'fresh', 'fruits']})
        print("[LOG] extract_conos after reset:", self.dp.extract_conos)

        # Temporary arrays
        self.dp.temp_data = {
            'boxes_temp': [],
            'weights_temp': [],
            'perbox_temp': [],
            'fresh_temp': [],
            'fruits_temp': []
        }

        # 1. SHIPPED ON BOARD DATE (1,11)
        for (page_num, block_num), block_data in self.dp.data_conos['title'].items():
            if block_num == 11:
                date_str = block_data['value'].strip()
                self.dp.extract_conos['EX_1_11_SOB_date'] = date_str
                try:
                    dt = self.de.parse_custom_date(date_str)
                    if dt:
                        self.dp.finish_conos['SOB_date'] = dt.strftime("%d.%m.%Y")
                    else:
                        self.dp.finish_conos['SOB_date'] = 'N/A'
                except Exception as e:
                    self.dp.finish_conos['SOB_date'] = 'N/A'
                    logging.error(f"Date parsing error: {date_str} - {str(e)}")

        # 2. Universal templates
        all_section = SEARCH_CONFIG.get("all", {})
        if isinstance(all_section, dict):
            for block_key, block_templates in all_section.items():
                print(f"\n[LOG] Universal search: {block_key}")
                self.de._process_block_templates(block_templates, block_key, format_type, shipper)

        # 3. Format templates
        format_section = SEARCH_CONFIG.get(format_type, {})
        if isinstance(format_section, dict):
            for block_key, block_templates in format_section.items():
                print(f"\n[LOG] Format search: {block_key}")
                self.de._process_block_templates(block_templates, block_key, format_type, shipper)

        # 4. Post-process temporary data
        print("\n[LOG] temp_data after search:", self.dp.temp_data)
        if self.dp.temp_data['boxes_temp']:
            self.dp.extract_conos['boxes'], self.dp.extract_conos['EX13_total_boxes'] = self.de.process_temp_list(
                self.dp.temp_data['boxes_temp'],
                len(self.dp.extract_conos['containers']),
                'boxes'
            )
            print(f"[LOG] extract_conos['boxes']: {self.dp.extract_conos['boxes']}, extract_conos['EX13_total_boxes']: {self.dp.extract_conos['EX13_total_boxes']}")
        if self.dp.temp_data['weights_temp']:
            self.dp.extract_conos['weights'], self.dp.extract_conos['EX14_total_GCW'] = self.de.process_temp_list(
                self.dp.temp_data['weights_temp'],
                len(self.dp.extract_conos['containers']),
                'weights'
            )
            print(f"[LOG] extract_conos['weights']: {self.dp.extract_conos['weights']}, extract_conos['EX14_total_GCW']: {self.dp.extract_conos['EX14_total_GCW']}")
        self.dp.extract_conos['perbox'] = self.dp.temp_data['perbox_temp'][:len(self.dp.extract_conos['containers'])]
        if self.dp.temp_data['fresh_temp']:
            self.dp.extract_conos['fresh'], _ = self.de.process_temp_list(
                self.dp.temp_data['fresh_temp'],
                len(self.dp.extract_conos['containers']),
                log_name='fresh',
                data_type='string'
            )
            print(f"[LOG] extract_conos['fresh']: {self.dp.extract_conos['fresh']}")
        if self.dp.temp_data['fruits_temp']:
            self.dp.extract_conos['fruits'], _ = self.de.process_temp_list(
                self.dp.temp_data['fruits_temp'],
                len(self.dp.extract_conos['containers']),
                log_name='fruits',
                data_type='string'
            )
            print(f"[LOG] extract_conos['fruits']: {self.dp.extract_conos['fruits']}")

        # 5. Update ROWS counters
        self.dp.rows_count['conos'].update({
            'total_cont': len(self.dp.extract_conos['containers']),
            'total_boxes': len(self.dp.extract_conos['boxes']),
            'total_weights': len(self.dp.extract_conos['weights']),
            'total_perbox': len(self.dp.extract_conos['perbox']),
            'total_fresh': len(self.dp.extract_conos['fresh']),
            'total_fruits': len(self.dp.extract_conos['fruits'])
        })
        print("[LOG] rows_count['conos']:", self.dp.rows_count['conos'])
        # 6. Align lists
        self.dp.align_container_lists()
        # 7. Calculations and checks
        self.dp.calculate_amounts()
        self.v.run_check_control()
        print("\n--- [LOG] End search_variables ---\n")

    # -------------------- Debug --------------------

    def print_debug_info(self):
        """Improved debug information output function"""
        SEPARATOR = "=" * 100
        SUBSEPARATOR = "-" * 100
        
        print("\n" + SEPARATOR)
        print("=== DEBUG INFORMATION ===".center(100))
        print(SEPARATOR + "\n")

        def safe_print_dict(name, data):
            print(f"● {name}:")
            print(SUBSEPARATOR)
            try:
                if data is None:
                    print("  [No data]")
                elif isinstance(data, dict):
                    if not data:
                        print("  [Empty dictionary]")
                    else:
                        for key, value in data.items():
                            if isinstance(value, (list, tuple, set)):
                                print(f"  {key} ({len(value)}):")
                                for i, item in enumerate(value, 1):
                                    print(f"    {i}. {item}")
                            elif isinstance(value, dict):
                                print(f"  {key}:")
                                for k, v in value.items():
                                    print(f"    {k}: {v}")
                            else:
                                print(f"  {key}: {value}")
                else:
                    print(f"  [Data type: {type(data).__name__}]")
                    print(f"  {str(data)}")
            except Exception as e:
                print(f"  [Output error: {str(e)}]")
            print()

        # Ensure finish dicts exist
        try:
            if not getattr(self.dp, 'finish_conos', None):
                self.dp.finish_conos = self.dp.create_finish_conos()
        except Exception as e:
            print(f"! Error creating finish_conos: {str(e)}")
            self.dp.finish_conos = None
        try:
            if not getattr(self.dp, 'finish_phito', None):
                self.dp.finish_phito = self.dp.create_finish_phito()
        except Exception as e:
            print(f"! Error creating finish_phito: {str(e)}")
            self.dp.finish_phito = None

        sections = [
            ("finish_conos (final bill of lading data)", self.dp.finish_conos),
            ("finish_phito (final phytosanitary data)", self.dp.finish_phito),
            ("data_conos (raw bill of lading data)", self.dp.data_conos),
            ("data_phito (raw phytosanitary data)", self.dp.data_phito),
            ("extract_conos (extracted bill of lading data)", self.dp.extract_conos),
            ("extract_phito (extracted phytosanitary data)", self.dp.extract_phito),
            ("check_in_conos (bill of lading checks)", self.dp.check_in_conos),
            ("check_in_phito (phytosanitary checks)", self.dp.check_in_phito),
            ("control_results (bill vs phyto comparison)", self.dp.control_results)
        ]

        for name, data in sections:
            safe_print_dict(name, data)

        print(SEPARATOR)
        print("=== END DEBUG ===".center(100))
        print(SEPARATOR + "\n")
