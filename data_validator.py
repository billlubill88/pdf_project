# ================= IMPORTS =================
import re
import logging
from datetime import datetime
from typing import Dict, Any, Tuple, Set, List
from configs.config_fruits import FRUIT_TRANSLATIONS
from configs.config_phytosanitary import PHYTO_CONTAINER_PATTERN

class DataValidator:
    def __init__(self, pdf_processor, data_processor):
        """
        Initialize DataValidator with references to both processors.
        
        Args:
            pdf_processor: Reference to the main PDFProcessor instance
            data_processor: Reference to the DataProcessor instance
        """
        self.pdf_processor = pdf_processor
        self.data_processor = data_processor
        
        # Ссылки на все данные из data_processor для удобства доступа
        self.extract_conos = data_processor.extract_conos
        self.extract_phito = data_processor.extract_phito
        self.data_conos = data_processor.data_conos
        self.data_phito = data_processor.data_phito
        self.rows_count = data_processor.rows_count
        self.check_in_conos = data_processor.check_in_conos
        self.check_in_phito = data_processor.check_in_phito
        self.amounts_conos = data_processor.amounts_conos
        self.finish_conos = data_processor.finish_conos
        self.finish_phito = data_processor.finish_phito
        self.control_results = data_processor.control_results
        
        self.logger = logging.getLogger(__name__)
        
    def check_na_values(self) -> None:
        """Check N/A values for both pages of phytosanitary certificate."""
        na_config = {
            'page1_vertical': {
                10: ('page1_vertical', 10),
                11: ('page1_vertical', 11),
                12: ('page1_vertical', 12),
                13: ('page1_vertical', 13),
                14: ('page1_vertical', 14)
            },
            'page2_horizontal': {
                8: ('page2_horizontal', 8),
                9: ('page2_horizontal', 9),
                10: ('page2_horizontal', 10),
                11: ('page2_horizontal', 11),
                12: ('page2_horizontal', 12)
            }
        }
        
        # Check for page 1
        for block_num, key in na_config['page1_vertical'].items():
            block_data = self.data_processor.data_phito.get(key, {})
            value = str(block_data.get('value', '')).strip().upper()
            self.data_processor.check_in_phito['check_NA_page1'][block_num] = any(
                na in value 
                for na in ['N/A']
            )
        
        # Check for page 2
        for block_num, key in na_config['page2_horizontal'].items():
            block_data = self.data_processor.data_phito.get(key, {})
            value = str(block_data.get('value', '')).strip().upper()
            self.data_processor.check_in_phito['check_NA_page2'][block_num] = any(
                na in value 
                for na in ['N/A']
            )

    def check_required_fields(self) -> None:
        """Check required fields completion for both pages of phytosanitary certificate."""
        # Configuration of checked blocks
        required_blocks = {
            'page1_vertical': {
                'place_of_issue': 16,
                'authorized_officer': 18
            },
            'page2_horizontal': {
                'place_of_issue': 16,
                'authorized_officer': 18
            }
        }

        # Check for page 1
        for field, block_num in required_blocks['page1_vertical'].items():
            key = ('page1_vertical', block_num)
            value = self.data_processor.data_phito.get(key, {}).get('value', '').strip()
            self.data_processor.check_in_phito['required_fields_page1'][field] = len(value) > 0 and value != 'N/A'

        # Check for page 2
        for field, block_num in required_blocks['page2_horizontal'].items():
            key = ('page2_horizontal', block_num)
            value = self.data_processor.data_phito.get(key, {}).get('value', '').strip()
            self.data_processor.check_in_phito['required_fields_page2'][field] = len(value) > 0 and value != 'N/A'

    def check_phytosanitary_control(self) -> Dict[str, Dict[str, Any]]:
        """Perform all checks for phytosanitary certificate data."""
        checks = {
            'check_netto': {'result': None, 'values': (None, None)},
            'check_gross': {'result': None, 'values': (None, None)},
            'check_fruit_es': {'result': None, 'values': (None, None)},
            'check_fruit_la': {'result': None, 'values': (None, None)},
            'check_maritime': {'result': None, 'values': (None, None)},
            'check_ex_leningrad': {'result': None, 'values': (None, None)},
            'rows_equal': {'result': None, 'values': (None, None)},
            'containers_match': {'result': None, 'values': (None, None)},
            'numbers_match': {'result': None, 'values': (None, None)},
            'boxes_match': {'result': None, 'values': (None, None)},
            'BOXES_match': {'result': None, 'values': (None, None)},
            'all_boxes_match': {'result': None, 'values': (None, None)},
            'check_fresh': {'result': None, 'values': (None, None)},
            'check_date_PHITO': {'result': None, 'values': (None, None)}
        }
        
        try:
            # Check maritime
            maritime_block = self.data_processor.data_phito.get(('page1_vertical', 4), {})
            maritime_text = maritime_block.get('value', '').upper()
            checks['check_maritime']['result'] = 'MARITIME' in maritime_text
            checks['check_maritime']['values'] = (maritime_text, 'MARITIME')

            # Check EX LENINGRAD
            point_of_entry_block = self.data_processor.data_phito.get(('page1_vertical', 5), {})
            point_of_entry_text = point_of_entry_block.get('value', '').upper()
            checks['check_ex_leningrad']['result'] = 'EX LENINGRAD' in point_of_entry_text
            checks['check_ex_leningrad']['values'] = (point_of_entry_text, 'EX LENINGRAD')

            # Main checks
            checks['check_netto']['result'] = (
                self.data_processor.extract_phito.get('EX_ph1_8_NETTO') == 
                self.data_processor.extract_phito.get('EX_ph2_6_NETTO')
            )
            checks['check_netto']['values'] = (
                self.data_processor.extract_phito.get('EX_ph1_8_NETTO'), 
                self.data_processor.extract_phito.get('EX_ph2_6_NETTO')
            )
            
            checks['check_gross']['result'] = (
                self.data_processor.extract_phito.get('EX_ph1_8_GROSS') == 
                self.data_processor.extract_phito.get('EX_ph2_7_GROSS')
            )
            checks['check_gross']['values'] = (
                self.data_processor.extract_phito.get('EX_ph1_8_GROSS'), 
                self.data_processor.extract_phito.get('EX_ph2_7_GROSS')
            )
            
            checks['check_fruit_es']['result'] = (
                self.data_processor.extract_phito.get('EX_ph1_8_fruta') == 
                self.data_processor.extract_phito.get('EX_ph2_4_fruta')
            )
            checks['check_fruit_es']['values'] = (
                self.data_processor.extract_phito.get('EX_ph1_8_fruta'), 
                self.data_processor.extract_phito.get('EX_ph2_4_fruta')
            )
            
            checks['check_fruit_la']['result'] = (
                self.data_processor.extract_phito.get('EX_ph1_9_fructus') == 
                self.data_processor.extract_phito.get('EX_ph2_4_fructus')
            )
            checks['check_fruit_la']['values'] = (
                self.data_processor.extract_phito.get('EX_ph1_9_fructus'), 
                self.data_processor.extract_phito.get('EX_ph2_4_fructus')
            )
            
            checks['rows_equal']['result'] = (
                self.data_processor.rows_count['phito'].get('total_cont_PH1') == 
                self.data_processor.rows_count['phito'].get('total_cont_PH2')
            )
            checks['rows_equal']['values'] = (
                self.data_processor.rows_count['phito'].get('total_cont_PH1'), 
                self.data_processor.rows_count['phito'].get('total_cont_PH2')
            )
            
            checks['containers_match']['result'] = (
                set(self.data_processor.extract_phito.get('Containers_PH_1', [])) == 
                set(self.data_processor.extract_phito.get('Containers_PH_2', []))
            )
            checks['containers_match']['values'] = (
                self.data_processor.extract_phito.get('Containers_PH_1'), 
                self.data_processor.extract_phito.get('Containers_PH_2')
            )
            
            checks['numbers_match']['result'] = (
                self.data_processor.extract_phito.get('page1_number') == 
                self.data_processor.extract_phito.get('page2_number')
            )
            checks['numbers_match']['values'] = (
                self.data_processor.extract_phito.get('page1_number'), 
                self.data_processor.extract_phito.get('page2_number')
            )

            # Checks for Box/BOXES
            checks['boxes_match']['result'] = (
                self.data_processor.extract_phito.get('PH1_Box', None) == 
                self.data_processor.extract_phito.get('PH2_Box', None)
            )
            checks['boxes_match']['values'] = (
                self.data_processor.extract_phito.get('PH1_Box'), 
                self.data_processor.extract_phito.get('PH2_Box')
            )
            
            checks['BOXES_match']['result'] = (
                self.data_processor.extract_phito.get('PH1_BOXES', None) == 
                self.data_processor.extract_phito.get('PH2_BOXES', None)
            )
            checks['BOXES_match']['values'] = (
                self.data_processor.extract_phito.get('PH1_BOXES'), 
                self.data_processor.extract_phito.get('PH2_BOXES')
            )

            # Complex Box/BOXES check
            checks['all_boxes_match']['result'] = (
                checks['boxes_match']['result'] and 
                checks['BOXES_match']['result']
            )
            checks['all_boxes_match']['values'] = (
                checks['boxes_match']['result'],
                checks['BOXES_match']['result']
            )
            
            # Check FRESH
            checks['check_fresh']['result'] = (
                self.data_processor.extract_phito.get('EX_ph1__15_fresh') == 
                self.data_processor.extract_phito.get('EX_ph2__15_fresh') == 
                'FRESH'
            )
            checks['check_fresh']['values'] = (
                self.data_processor.extract_phito.get('EX_ph1__15_fresh'), 
                self.data_processor.extract_phito.get('EX_ph2__15_fresh')
            )
            
            # Check phytosanitary dates
            date1 = self.data_processor.extract_phito.get('EX_1_17_Date_PHITO', '')
            date2 = self.data_processor.extract_phito.get('EX_2_17_Date_PHITO', '')
            checks['check_date_PHITO']['result'] = (date1 == date2)
            checks['check_date_PHITO']['values'] = (date1, date2)
            
            # Parse and save phytosanitary date
            if checks['check_date_PHITO']['result'] and date1:
                dt = self.data_processor.data_extractor.parse_custom_date(date1)
                if dt:
                    self.data_processor.finish_phito['date_phito'] = dt.strftime("%d.%m.%Y")
                else:
                    self.data_processor.finish_phito['date_phito'] = 'N/A'
            else:
                self.data_processor.finish_phito['date_phito'] = 'N/A'
                
        except Exception as e:
            self.logger.error(f"Error during checks: {str(e)}", exc_info=True)
        
        # Update global dictionary
        for check_name in checks:
            self.data_processor.check_in_phito[check_name] = checks[check_name]['result']
        
        # Additional checks
        self.check_na_values()
        self.check_required_fields()
        self.data_processor.create_finish_phito()
        
        return checks

    def perform_control_checks(self) -> Dict[str, Dict[str, Any]]:
        """Perform all control checks between bill of lading and phytosanitary."""
        def normalize_text(text: str) -> List[str]:
            """Normalize text for comparison."""
            if not text:
                return []
            # Convert to lowercase and remove special chars
            cleaned = re.sub(r'[^\w\s]', ' ', str(text).lower())
            # Remove multiple spaces and split to words
            return [word for word in re.sub(r'\s+', ' ', cleaned).strip().split() if word]

        # Initialize result structure
        self.data_processor.control_results = {
            'Exporter': {},
            'Consignee': {},
            'Vessel_Voyage': {},
            'Port_Discharge': {},
            'control_check': {
                'CC_Exporter': False,
                'CC_Consignee': False,
                'CC_Vessel_Voyage': False,
                'CC_Port_Discharge': False
            }
        }

        # 1. Check Exporter
        conos_exporter = self.data_processor.data_conos['title'].get((1, 3), {}).get('value', '')
        phyto_exporter = self.data_processor.data_phito.get(('page1_vertical', 1), {}).get('value', '')
        conos_words = set(normalize_text(conos_exporter))
        phyto_words = set(normalize_text(phyto_exporter))
        
        self.data_processor.control_results['Exporter'] = {
            'match': conos_words == phyto_words,
            'matched_words': list(conos_words & phyto_words),
            'unmatched_words_conos': list(conos_words - phyto_words),
            'unmatched_words_phito': list(phyto_words - conos_words),
            'conos_source': f"B/L Block (1,3): {conos_exporter}",
            'phito_source': f"Phyto Block (1,1): {phyto_exporter}"
        }
        self.data_processor.control_results['control_check']['CC_Exporter'] = self.data_processor.control_results['Exporter']['match']

        # 2. Check Consignee
        conos_consignee = self.data_processor.data_conos['title'].get((1, 4), {}).get('value', '')
        phyto_consignee = self.data_processor.data_phito.get(('page1_vertical', 2), {}).get('value', '')
        conos_words = set(normalize_text(conos_consignee))
        phyto_words = set(normalize_text(phyto_consignee))
        
        self.data_processor.control_results['Consignee'] = {
            'match': conos_words == phyto_words,
            'matched_words': list(conos_words & phyto_words),
            'unmatched_words_conos': list(conos_words - phyto_words),
            'unmatched_words_phito': list(phyto_words - conos_words),
            'conos_source': f"B/L Block (1,4): {conos_consignee}",
            'phito_source': f"Phyto Block (1,2): {phyto_consignee}"
        }
        self.data_processor.control_results['control_check']['CC_Consignee'] = self.data_processor.control_results['Consignee']['match']

        # 3. Check Vessel_Voyage
        conos_vessel = self.data_processor.data_conos['title'].get((1, 6), {}).get('value', '')
        phyto_vessel = self.data_processor.data_phito.get(('page1_vertical', 6), {}).get('value', '')
        conos_words = set(normalize_text(conos_vessel))
        phyto_words = set(normalize_text(phyto_vessel))
        
        self.data_processor.control_results['Vessel_Voyage'] = {
            'match': conos_words.issubset(phyto_words),
            'matched_words': list(conos_words & phyto_words),
            'unmatched_words_conos': list(conos_words - phyto_words),
            'unmatched_words_phito': list(phyto_words - conos_words),
            'conos_source': f"B/L Block (1,6): {conos_vessel}",
            'phito_source': f"Phyto Block (1,6): {phyto_vessel}"
        }
        self.data_processor.control_results['control_check']['CC_Vessel_Voyage'] = self.data_processor.control_results['Vessel_Voyage']['match']

        # 4. Check Port_Discharge
        conos_port = self.data_processor.data_conos['title'].get((1, 8), {}).get('value', '')
        phyto_port = self.data_processor.data_phito.get(('page1_vertical', 5), {}).get('value', '')
        conos_words = set(self.normalize_port(conos_port).split())
        phyto_words = set(self.normalize_port(phyto_port).split())
        
        self.data_processor.control_results['Port_Discharge'] = {
            'match': conos_words == phyto_words,
            'matched_words': list(conos_words & phyto_words),
            'unmatched_words_conos': list(conos_words - phyto_words),
            'unmatched_words_phito': list(phyto_words - conos_words),
            'conos_source': f"B/L Block (1,8): {conos_port}",
            'phito_source': f"Phyto Block (1,5): {phyto_port}"
        }
        self.data_processor.control_results['control_check']['CC_Port_Discharge'] = self.data_processor.control_results['Port_Discharge']['match']
        
        return self.data_processor.control_results

    def compare_conos_phito(self) -> Dict[str, bool]:
        """Compare bill of lading and phytosanitary data."""
        control_check = {}
        
        # 1. Containers
        containers_conos = set(self.data_processor.finish_conos.get('containers_conos', []))
        containers_phito = set(self.data_processor.finish_phito.get('containers_phito', []))
        control_check['CC_containers'] = containers_conos == containers_phito
        
        # 2. Container count
        control_check['CC_total_cont'] = (
            self.data_processor.finish_conos.get('total_cont_conos', 0) == 
            self.data_processor.finish_phito.get('total_cont_phito', 0)
        )
        
        # 3. Box count
        control_check['CC_boxes'] = (
            self.data_processor.finish_conos.get('boxes_conos', 0) == 
            self.data_processor.finish_phito.get('boxes_phito', 0)
        )
        
        # 4. Average weight per box
        gross_perbox_conos = self.data_processor.finish_conos.get('gross_perbox_conos', 0.0)
        gross_perbox_phito = self.data_processor.finish_phito.get('gross_perbox_phito', 0.0)
        control_check['CC_gross_perbox'] = (
            abs(float(gross_perbox_conos) - float(gross_perbox_phito)) <= 0.01
        )
        
        # 5. Total weight
        gross_conos = self.data_processor.finish_conos.get('gross_conos', 0.0)
        gross_phito = self.data_processor.finish_phito.get('gross_phito', 0.0)
        control_check['CC_gross_weight'] = (
            abs(float(gross_conos) - float(gross_phito)) <= 0.1
        )
        
        # 6. FRESH
        fresh_conos = 'FRESH' in self.data_processor.finish_conos.get('fresh_conos', [])
        fresh_phito = self.data_processor.finish_phito.get('fresh_phito') == 'FRESH'
        control_check['CC_fresh'] = fresh_conos == fresh_phito
        
        # 7. Fruits (English)
        fruit_eng_conos = set(self.data_processor.finish_conos.get('fruit_eng_conos', []))
        fruit_eng_phito = {self.data_processor.finish_phito.get('fruit_eng_phito', '')}
        control_check['CC_fruit'] = (
            len(fruit_eng_conos) == 1 and 
            fruit_eng_conos == fruit_eng_phito
        )
        
        # 8-11. Previous check results (including CC_Port_Discharge)
        if 'control_check' in self.data_processor.control_results:
            control_check.update({
                'CC_Exporter': self.data_processor.control_results['control_check'].get('CC_Exporter', False),
                'CC_Consignee': self.data_processor.control_results['control_check'].get('CC_Consignee', False),
                'CC_Vessel_Voyage': self.data_processor.control_results['control_check'].get('CC_Vessel_Voyage', False),
                'CC_Port_Discharge': self.data_processor.control_results['control_check'].get('CC_Port_Discharge', False)
            })

        # Date check
        try:
            sob_date_str = self.data_processor.finish_conos.get('SOB_date', 'N/A')
            phito_date_str = self.data_processor.finish_phito.get('date_phito', 'N/A')
            
            if sob_date_str != 'N/A' and phito_date_str != 'N/A':
                sob_date = datetime.strptime(sob_date_str, "%d.%m.%Y")
                phito_date = datetime.strptime(phito_date_str, "%d.%m.%Y")
                control_check['CC_date'] = sob_date >= phito_date
                
        except Exception as e:
            self.logger.error(f"Date comparison error: {str(e)}", exc_info=True)
            control_check['CC_date'] = False
        
        # Save to global results
        self.data_processor.control_results['control_check'] = control_check
        return control_check

    def run_check_control(self) -> None:
        """Check bill of lading control values."""
        # Check #1: EX9_qty_CONT_CARRIERS is number
        try:
            val = int(self.data_processor.extract_conos['EX9_qty_CONT_CARRIERS'])
            self.data_processor.check_in_conos['EX9_is_number'] = val != 0
        except (ValueError, KeyError):
            self.data_processor.check_in_conos['EX9_is_number'] = False
        
        # Check #2: EX13_qty_CONT is number
        try:
            val = int(self.data_processor.extract_conos['EX13_qty_CONT'])
            self.data_processor.check_in_conos['EX13_qty_is_number'] = val != 0
        except (ValueError, KeyError):
            self.data_processor.check_in_conos['EX13_qty_is_number'] = False

        # Check #4: EX13_qty_CONT == EX9_qty_CONT_CARRIERS
        try:
            self.data_processor.check_in_conos['EX13_qty_CONT'] = (
                int(self.data_processor.extract_conos['EX13_qty_CONT']) == 
                int(self.data_processor.extract_conos['EX9_qty_CONT_CARRIERS']))
        except (ValueError, KeyError):
            self.data_processor.check_in_conos['EX13_qty_CONT'] = False

        # Check #8: EX13_total_items == SUM_boxes
        try:
            self.data_processor.check_in_conos['EX13_total_items'] = (
                int(self.data_processor.extract_conos['EX13_total_items']) == 
                self.data_processor.amounts_conos['SUM_boxes'])
        except (ValueError, KeyError):
            self.data_processor.check_in_conos['EX13_total_items'] = False

        # Check #9: EX14_total_GCW == SUM_weights
        try:
            val1 = float(str(self.data_processor.extract_conos['EX14_total_GCW']).replace(',', '.'))
            val2 = float(str(self.data_processor.amounts_conos['AM_total_weight']).replace(',', '.'))
            self.data_processor.check_in_conos['EX14_total_GCW'] = abs(val1 - val2) < 0.01
        except (ValueError, KeyError, TypeError):
            self.data_processor.check_in_conos['EX14_total_GCW'] = False

        # Check #11: Element-wise comparison of AM_weight and weights
        self.data_processor.check_in_conos['weights'] = {}
        try:
            for i, (am, w) in enumerate(zip(self.data_processor.amounts_conos['AM_weight'], 
                                          self.data_processor.extract_conos['weights'])):
                self.data_processor.check_in_conos['weights'][i] = float(am) == float(w)
        except (KeyError, IndexError, ValueError):
            pass

        # New check: Compare all ROWS with each other
        row_values = list(self.data_processor.rows_count['conos'].values())
        self.data_processor.check_in_conos['rows_equally'] = all(v == row_values[0] for v in row_values)

        # Check #12: Compare ROWS elements with EX9/EX13 (if rows not equal)
        self.data_processor.check_in_conos['rows_individual'] = {}
        if not self.data_processor.check_in_conos['rows_equally']:
            target_value = None
            
            # Determine target value for comparison
            if self.data_processor.check_in_conos.get('EX9_is_number', False):
                try:
                    target_value = int(self.data_processor.extract_conos['EX9_qty_CONT_CARRIERS'])
                except (ValueError, KeyError):
                    pass
            elif self.data_processor.check_in_conos.get('EX13_qty_is_number', False):
                try:
                    target_value = int(self.data_processor.extract_conos['EX13_qty_CONT'])
                except (ValueError, KeyError):
                    pass
            
            # If valid target value found - perform comparison
            if target_value is not None:
                self.data_processor.check_in_conos['rows_individual'] = {
                    key: (value == target_value) 
                    for key, value in self.data_processor.rows_count['conos'].items()
                }

    def normalize_port(self, text: str) -> str:
        """Normalize text for port comparison."""
        # Remove EX LENINGRAD and RUSSIA/Russian Federation
        text = re.sub(r'\(EX LENINGRAD\)', '', text, flags=re.IGNORECASE)
        # Replace abbreviations
        text = re.sub(r'\bST\b', 'Saint', text, flags=re.IGNORECASE)
        text = re.sub(r'\bPETERSBURG\b', 'Petersburg', text, flags=re.IGNORECASE)
        text = re.sub(r'\bRUSSIA\b', 'Russian Federation', text, flags=re.IGNORECASE)      
        # Remove special chars and convert to lowercase
        return re.sub(r'[^\w\s]', '', text).strip().lower()
