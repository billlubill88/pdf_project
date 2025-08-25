import re
import logging
from datetime import datetime
from typing import Optional, Tuple, Dict, List, Union
import pdfplumber
from pdfplumber.page import Page

from configs.config_phytosanitary import PHYTOSANITARY_CONFIG, PHYTO_CONTAINER_PATTERN
from configs.config_fruits import FRUITS, FRUIT_TRANSLATIONS

class DataExtractor:
    def __init__(self, processor):
        self.processor = processor
        self.visualizer = processor.visualizer

    def extract_shipper_name(self, shipper_text: str) -> Optional[str]:
        """Extract standardized shipper name from text"""
        shipper_text_up = shipper_text.upper()
        known_shippers = [
            'EXPORTADORA DE BANANO',
            'GREEN EXPRESS',
            'FRIENDLY ORGANIC',
            'ECUAGREENPRODEX',
            'REYBANPAC',
            'BAGATOCORP',
            'HACIENDA GUAYABO GUAYABOSA',
        ]
        for name in known_shippers:
            if name in shipper_text_up:
                return name
        return None

    def get_text_objects(self, page: Page, coords: Tuple[float, float, float, float]) -> str:
        """Extract text within given page coordinates"""
        (x0, top, x1, bottom) = coords
        words = page.extract_words()
        
        result = []
        for word in words:
            if (word['x0'] >= x0 and word['x1'] <= x1 and 
                word['top'] >= top and word['bottom'] <= bottom):
                result.append(word['text'])
        
        return ' '.join(result)

    def determine_format(self, block0_text: str, num_pages: int) -> str:
        """Determine bill of lading type by first page text and number of pages"""
        text_upper = (block0_text or "").upper()

        if "STANDARD EDITION - 01/2017" in text_upper:
            fmt = "GOST-Multi" if num_pages > 1 else "GOST-Mono"
        elif ('CODE_NAME:' in text_upper and 'CONGENBILL' in text_upper and 'EDITION 1994' in text_upper) \
             or ('CONGENBILL' in text_upper and 'EDITION 1994' in text_upper):
            fmt = "CHARTER"
        elif "STANDARD EDITION - 02/2015" in text_upper:
            fmt = "CURSIV"
        elif "SCAC CODE: MSCU" in text_upper:
            fmt = "DOSYL"
        else:
            fmt = "UNKNOWN"

        return fmt

    def determine_phytosanitary_format(self, pdf: pdfplumber.PDF) -> str:
        """Determine phytosanitary certificate format"""
        first_page = pdf.pages[0]
        
        # Check Country block
        country_block = PHYTOSANITARY_CONFIG["ECUADOR"]["page1_vertical"][0]
        coords = self.visualizer.calculate_pdf_coordinates(first_page, country_block)
        text = self.get_text_objects(first_page, coords).upper()
        
        # Search by keywords
        ecuador_keywords = r"ECUADOR|ECUATORIANO|ANDINO|MAGAP|AGROCALIDAD"
        if re.search(ecuador_keywords, text):
            return "ECUADOR"
        
        return "ECUADOR"  # Default

    def find_block_by_text(self, page: Page, search_phrases: List[str]) -> Optional[Tuple[float, float, float, float]]:
        """Find block coordinates containing any of the search phrases"""
        words = page.extract_words()
        matches = []
        
        for i, word in enumerate(words):
            for phrase in search_phrases:
                if phrase.lower() in word['text'].lower():
                    matches.append((word['x0'], word['top'], word['x1'], word['bottom']))
        
        if not matches:
            return None
            
        # Determine common block boundaries
        x0 = min(match[0] for match in matches)
        top = min(match[1] for match in matches)
        x1 = max(match[2] for match in matches)
        bottom = max(match[3] for match in matches)
        
        return (x0, top, x1, bottom)

    def detect_table(self, page: Page, header_phrases: List[str]) -> Optional[Dict[str, float]]:
        """Detect table coordinates based on header phrases"""
        header_coords = self.find_block_by_text(page, header_phrases)
        
        if not header_coords:
            return None
        
        # Expand search area down to next block or page end
        table_bottom = self.processor.data_processor.visualizer.find_next_block_top(page, header_coords[3])
        
        return {
            'x0': header_coords[0],
            'top': header_coords[1],
            'x1': page.width - 10,  # Right page border
            'bottom': table_bottom
        }

    def extract_phytosanitary_values(self) -> None:
        """Extract and process data from phytosanitary certificate"""
        def safe_extract_number(pattern: str, text: str) -> Optional[float]:
            """Extract number from text - always returns float!"""
            try:
                match = re.search(pattern, text or '', re.IGNORECASE)
                if match:
                    value = match.group(1).replace(',', '.').replace(' ', '')
                    return float(value)
                return None
            except Exception:
                return None

        def find_fruit(text: str) -> Optional[Dict[str, str]]:
            """Find fruit in text and return translations"""
            try:
                text = text or ''
                for fruit in FRUITS:
                    if (re.search(rf'\b{re.escape(fruit)}\b', text, re.IGNORECASE) or 
                        re.search(rf'\b{re.escape(FRUIT_TRANSLATIONS[fruit]["es"])}\b', text, re.IGNORECASE)):
                        return FRUIT_TRANSLATIONS[fruit]
                return None
            except:
                return None

        # Process phytosanitary data
        for key, block_data in self.processor.data_processor.data_phito.items():
            if not isinstance(key, tuple) or len(key) != 2:
                continue
                
            page_type, block_num = key
            text = block_data.get('value', '')
            
            # Vertical page
            if page_type == 'page1_vertical':
                if block_num == 8:  # Name and quantity
                    self.processor.data_processor.extract_phito['EX_ph1_8_NETTO'] = safe_extract_number(r'Net\s*Weight:\s*(\d[\d,\.]*)', text)
                    self.processor.data_processor.extract_phito['EX_ph1_8_GROSS'] = safe_extract_number(r'Gross\s*Weight:\s*(\d[\d,\.]*)', text)
                    
                    fruit = find_fruit(text)
                    if fruit:
                        self.processor.data_processor.extract_phito['EX_ph1_8_fruta'] = fruit['es']
                
                elif block_num == 9:  # Botanical name
                    self.processor.data_processor.extract_phito['EX_ph1_9_fructus'] = text.strip()
                
                elif block_num == 7:  # Box quantity
                    self.processor.data_processor.extract_phito['PH1_Box'] = safe_extract_number(r'(\d+)\s*Box', text)
                
                elif block_num == 15:  # Additional information
                    self.processor.data_processor.extract_phito['PH1_BOXES'] = safe_extract_number(r'(\d[\d\.]*)\s*BOXES', text)
                    if re.search(r'\bFRESH\b', text, re.IGNORECASE):
                        self.processor.data_processor.extract_phito['EX_ph1__15_fresh'] = 'FRESH'
            
            # Horizontal page
            elif page_type == 'page2_horizontal':
                if block_num == 4:  # Product info
                    fruit = find_fruit(text)
                    if fruit:
                        self.processor.data_processor.extract_phito['EX_ph2_4_fruta'] = fruit['es']
                        self.processor.data_processor.extract_phito['EX_ph2_4_fructus'] = fruit['la']
                
                elif block_num == 6:  # Net Weight
                    self.processor.data_processor.extract_phito['EX_ph2_6_NETTO'] = safe_extract_number(r'(\d[\d,\.]*)', text)
                
                elif block_num == 7:  # Gross Weight
                    self.processor.data_processor.extract_phito['EX_ph2_7_GROSS'] = safe_extract_number(r'(\d[\d,\.]*)', text)
                
                elif block_num == 5:  # Box quantity
                    self.processor.data_processor.extract_phito['PH2_Box'] = safe_extract_number(r'(\d+)\s*Box', text)
                
                elif block_num == 15:  # Adicional Information
                    self.processor.data_processor.extract_phito['PH2_BOXES'] = safe_extract_number(r'(\d[\d\.]*)\s*BOXES', text)
                    if re.search(r'\bFRESH\b', text, re.IGNORECASE):
                        self.processor.data_processor.extract_phito['EX_ph2__15_fresh'] = 'FRESH'

    def parse_custom_date(self, date_str: str) -> Optional[datetime]:
        """Parse date from various formats with weekday handling"""
        if not date_str or not isinstance(date_str, str):
            return None

        # Remove weekdays
        date_str = re.sub(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)[,\s]*', 
                         '', 
                         date_str.strip(), 
                         flags=re.IGNORECASE)
        
        # Remove extra spaces
        date_str = re.sub(r'\s+', ' ', date_str.strip())
        
        # List of possible date formats
        date_formats = [
            "%d-%b-%Y",    # 27-Feb-2025
            "%d %b %Y",     # 27 Feb 2025
            "%d.%m.%Y",     # 27.02.2025
            "%d/%m/%Y",     # 27/02/2025
            "%Y-%m-%d",     # 2025-02-27
            "%B %d, %Y",    # February 27, 2025
            "%b %d, %Y",    # Feb 27, 2025
            "%m/%d/%Y",     # 02/27/2025
            "%d %B %Y",     # 27 February 2025
            "%Y%m%d"       # 20250227
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None

    def safe_divide(self, a: float, b: float) -> float:
        """Safe division with zero handling"""
        return a / b if b != 0 else 0

    def process_temp_list(self, temp_list: List[Union[str, int, float]], target_len: int, 
                         log_name: str = '', data_type: str = 'number') -> Tuple[List, Optional[Union[int, float, str]]]:
        """
        Process temporary data list with type conversion and length alignment
        Returns tuple: (processed_list, final_value)
        """
        processed = []
        final_value = None
        default_value = 0 if data_type == 'number' else 'N/A'

        try:
            for idx, item in enumerate(temp_list):
                try:
                    if data_type == 'number':
                        cleaned = str(item).strip().replace(',', '')
                        val = float(cleaned) if '.' in cleaned else int(cleaned)
                    else:
                        val = str(item).strip().upper()
                    processed.append(val)
                except (ValueError, TypeError):
                    processed.append(default_value)

            # Handle length discrepancies
            diff = len(processed) - target_len
            if diff == 1:
                final_value = processed[-1]
                processed = processed[:-1]
            elif diff > 1:
                processed = processed[:target_len]
            elif diff < 0:
                processed += [default_value] * abs(diff)

            # Final length check
            if len(processed) != target_len:
                processed = processed[:target_len] + [default_value] * (target_len - len(processed))

        except Exception as e:
            logging.error(f"Error processing {log_name} list: {str(e)}")
            processed = [default_value] * target_len

        return processed, final_value

    def _process_block_templates(self, block_templates: List[Dict], block_key: str, 
                               format_type: str, shipper: Optional[str]) -> None:
        """
        Process block templates to extract data from text
        """
        source = self.processor.data_processor.data_conos['title'] if block_key.lower().startswith("title") else self.processor.data_processor.data_conos['rider']
        
        for template in block_templates:
            for (page_num, block_num), block_data in source.items():
                if block_num != template.get("block"):
                    continue
                    
                text = block_data['value']
                
                # Apply minus phrases
                minus_phrases = []
                minus_cfg = template.get('minus_phrase')
                if isinstance(minus_cfg, dict):
                    if shipper and shipper in minus_cfg:
                        minus_phrases += minus_cfg[shipper]
                    if format_type in minus_cfg:
                        minus_phrases += minus_cfg[format_type]
                    if 'all' in minus_cfg:
                        minus_phrases += minus_cfg['all']
                elif minus_cfg:
                    minus_phrases = minus_cfg if isinstance(minus_cfg, list) else [minus_cfg]
                
                for phrase in minus_phrases:
                    text = text.replace(phrase, '').strip()

                # Get pattern based on priority
                pattern = None
                pat_cfg = template['pattern']
                if isinstance(pat_cfg, dict):
                    if shipper and shipper in pat_cfg:
                        pattern = pat_cfg[shipper]
                    elif format_type in pat_cfg:
                        pattern = pat_cfg[format_type]
                    elif 'all' in pat_cfg:
                        pattern = pat_cfg['all']
                else:
                    pattern = pat_cfg

                if not pattern:
                    continue

                flags = template.get('flags', 0)
                validation = template.get('validation')

                try:
                    # Container extraction
                    if template['type'] == 'cont':
                        for match in re.finditer(pattern, text, flags):
                            value = match.group(1)
                            if validation is None or re.fullmatch(validation, value):
                                self.processor.data_processor.extract_conos['containers'].append(value)
                    
                    # Special handling for per_box
                    elif template['type'] == 'per_box':
                        matches = re.findall(pattern, text, flags)
                        print(f"[LOG] Found per_box: {matches}")
                        if not matches:
                            continue
                        temp_values = []
                        prev_value = None
                        for value in matches:
                            try:
                                current = float(value.replace(',', '.'))
                                if prev_value is None:
                                    temp_values.append(current)
                                    prev_value = current
                                else:
                                    if current > prev_value:
                                        temp_values[-1] = current
                                        prev_value = current
                                    elif current == prev_value:
                                        temp_values.append(current)
                                        prev_value = current
                            except ValueError:
                                continue
                        self.processor.data_processor.temp_data['perbox_temp'].extend(temp_values)
                    
                    # Other data types
                    else:
                        matches = re.findall(pattern, text, flags)
                        if not matches:
                            continue

                        if template.get('target') == 'EXTRACT':
                            self.processor.data_processor.extract_conos[template['var_name']] = matches[-1]
                            continue
                            
                        temp_key = {
                            'box': 'boxes_temp',
                            'weight': 'weights_temp',
                            'fresh': 'fresh_temp',
                            'fruits': 'fruits_temp'
                        }.get(template['type'])
                        
                        if temp_key:
                            processed_values = []
                            for value in matches:
                                if template['type'] == 'box':
                                    processed = int(value) if value.isdigit() else 0
                                elif template['type'] == 'weight':
                                    processed = value.replace('.000', '').replace(',', '')
                                else:
                                    processed = value.upper()
                                processed_values.append(processed)
                            self.processor.data_processor.temp_data[temp_key].extend(processed_values)

                except Exception as e:
                    logging.error(f"Error processing template {template.get('var_name')}: {str(e)}")

