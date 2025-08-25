import re
import logging
from datetime import datetime
from configs.config_fruits import FRUIT_TRANSLATIONS

class DataProcessor:
    def __init__(self, data_extractor):
        self.data_extractor = data_extractor
        self.init_global_variables()
    
    def init_global_variables(self):
        """Initialize all global variables as instance attributes"""
        self.data_conos = {'title': {}, 'rider': {}}
        self.data_phito = {'page1_vertical': {}, 'page2_horizontal': {}}
        
        self.extract_conos = {
            'containers': [],
            'boxes': [],
            'weights': [],
            'perbox': [],
            'fresh': [],
            'fruits': [],
            'EX9_qty_CONT_CARRIERS': 'N/A',
            'EX13_qty_CONT': 'N/A',
            'EX14_total_GCW': 'N/A',
            'EX13_total_items': 'N/A',
            'total_fresh': 0,
            'total_fruits': 0,
            'EX_1_11_SOB_date': None
        }

        self.extract_phito = {
            'Containers_PH_1': [],
            'Containers_PH_2': [],
            'EX_ph1_8_NETTO': None,
            'EX_ph1_8_GROSS': None,
            'EX_ph2_6_NETTO': None,
            'EX_ph2_7_GROSS': None,
            'EX_ph1_8_fruta': None,
            'EX_ph1_9_fructus': None,
            'EX_ph2_4_fruta': None,
            'EX_ph2_4_fructus': None,
            'PH1_Box': None,
            'PH1_BOXES': None,
            'PH2_Box': None,
            'PH2_BOXES': None,
            'page1_number': None,
            'page2_number': None,
            'EX_1_17_Date_PHITO': None,
            'EX_2_17_Date_PHITO': None
        }
        
        self.check_in_conos = {
            'EX9_is_number': False,
            'EX13_qty_is_number': False,
            'EX13_qty_CONT': False,
            'EX14_total_GCW': False,
            'EX13_total_items': False,
            'rows_equally': False,
            'rows_individual': {},
            'weights': {}
        }
        
        self.check_in_phito = {
            'check_number': False,
            'check_netto': False,
            'check_gross': False,
            'check_fruit_es': False,
            'check_fruit_la': False,
            'check_fresh': False,
            'rows_equal': False,
            'containers_match': False,
            'numbers_match': False,
            'boxes_match': False,
            'BOXES_match': False,
            'all_boxes_match': False,
            'check_maritime': False,
            'check_NA_page1': {
                10: False, 11: False, 12: False, 13: False, 14: False
            },
            'check_NA_page2': {
                8: False, 9: False, 10: False, 11: False, 12: False
            },
            'required_fields_page1': {
                'place_of_issue': False,
                'authorized_officer': False
            },
            'required_fields_page2': {
                'place_of_issue': False,
                'authorized_officer': False
            }
        }

        self.rows_count = {
            'conos': {
                'total_cont': 0, 'total_boxes': 0,
                'total_weights': 0, 'total_perbox': 0,
                'total_fresh': 0, 'total_fruits': 0
            },
            'phito': {
                'total_cont_PH1': 0, 'total_cont_PH2': 0
            }
        }
        
        self.control_results = {}
        self.amounts_conos = {
            'SUM_boxes': 0, 'MID_perbox': 0.0,
            'SUM_weights': 0, 'AM_weight': [],
            'AM_total_weight': 0
        }

        self.finish_conos = {}
        self.finish_phito = {}
        
        self.temp_data = {
            'boxes_temp': [],
            'weights_temp': [],
            'perbox_temp': [],
            'fresh_temp': [],
            'fruits_temp': []
        }

    def process_temp_list(self, temp_list, target_len, log_name='', data_type='number'):
        """
        Universal processing of temporary data lists
        Supports numeric and string values
        """
        processed = []
        final_value = None
        default_value = 0 if data_type == 'number' else 'N/A'

        # Logging input
        print(f"\n🔧 Start processing {log_name}:")
        print(f"Source data ({len(temp_list)}): {temp_list}")
        print(f"Expected length: {target_len}, Data type: {data_type}")

        try:
            for idx, item in enumerate(temp_list):
                try:
                    # Main processing logic
                    if data_type == 'number':
                        # Convert numeric values
                        cleaned = str(item).strip().replace(',', '')
                        if '.' in cleaned:
                            val = float(cleaned)
                        else:
                            val = int(cleaned)
                    else:
                        # Process string values
                        val = str(item).strip().upper()
                    
                    processed.append(val)
                    
                except (ValueError, TypeError) as e:
                    # Conversion error handling
                    error_msg = f"Conversion error for item {idx}: '{item}' ({type(e).__name__})"
                    print(f"⚠ {error_msg}")
                    processed.append(default_value)

            # Calculate discrepancy
            diff = len(processed) - target_len
            print(f"Calculated discrepancy: {diff}")

            # Handle discrepancies
            if diff == 1:
                final_value = processed[-1]
                processed = processed[:-1]
                print(f"📌 Extracted final value: {final_value}")
            elif diff > 1:
                print(f"⚠ Trimmed {diff} items")
                processed = processed[:target_len]
            elif diff < 0:
                fill_value = default_value if data_type == 'number' else 'N/A'
                processed += [fill_value] * abs(diff)
                print(f"⚠ Added {abs(diff)} values {fill_value}")

            # Type check
            if data_type == 'number':
                type_check = all(isinstance(x, (int, float)) for x in processed)
            else:
                type_check = all(isinstance(x, str) for x in processed)
            
            if not type_check:
                print(f"⚠ Mixed types found in {log_name} list!")

        except Exception as e:
            print(f"💥 Critical error processing {log_name}: {str(e)}")
            processed = [default_value] * target_len

        # Final check
        if len(processed) != target_len:
            print(f"⚠ Final length mismatch! ({len(processed)} instead of {target_len})")
            processed = processed[:target_len] + [default_value] * (target_len - len(processed))

        # Final logging
        print(f"Processing result {log_name}:")
        print(f"Processed items: {len(processed)}")
        print(f"Sample values: {processed[:3]}...")  # Show first 3 items as example
        
        return processed, final_value

    def align_container_lists(self):
        """Align all lists to container count"""
        target_len = self.rows_count['conos']['total_cont']
        
        for key in ['boxes', 'weights', 'perbox', 'fresh', 'fruits']:
            current_len = len(self.extract_conos[key])
            if current_len < target_len:
                diff = target_len - current_len
                self.extract_conos[key] += [0] * diff
                print(f"Added {diff} zeros for {key}")

    def calculate_amounts(self):
        """Calculate total values with rounding"""
        # Convert boxes and perbox to numbers
        try:
            boxes = [int(b) for b in self.extract_conos['boxes']]
        except (ValueError, TypeError):
            boxes = self.extract_conos['boxes']
        
        try:
            # Round perbox to 2 decimal places before calculations
            perbox = [round(float(p), 2) if isinstance(p, (str, float)) else p for p in self.extract_conos['perbox']]
        except (ValueError, TypeError):
            perbox = self.extract_conos['perbox']
        
        sum_boxes = sum(boxes)
        sum_perbox = sum(perbox)
        
        # Round average to 2 decimal places
        mid_perbox = round(self.safe_divide(sum_perbox, len(perbox)), 2) if len(perbox) > 0 else 0.00
        
        # Calculations with result rounding
        self.amounts_conos.update({
            'SUM_boxes': sum_boxes,
            'MID_perbox': mid_perbox,
            'SUM_weights': round(sum(float(str(w).replace(',', '')) for w in self.extract_conos['weights']), 2),
            'AM_weight': [round(b * p, 2) for b, p in zip(boxes, perbox)],
            'AM_total_weight': round(sum_boxes * mid_perbox, 2)
        })
        
        # Update FRESH and FRUITS counters
        self.extract_conos['total_fresh'] = len([f for f in self.extract_conos['fresh'] if f != 'N/A'])
        self.extract_conos['total_fruits'] = len([f for f in self.extract_conos['fruits'] if f != 'N/A'])

    def safe_divide(self, numerator, denominator):
        """Safe division with zero check"""
        if denominator == 0:
            return 0
        return numerator / denominator

    def create_finish_conos(self):
        """Create final bill of lading data dictionary"""
        self.finish_conos = {}
        
        # 1. Unique containers
        self.finish_conos['containers_conos'] = tuple(set(self.extract_conos.get('containers', [])))
        
        # 2. Total container count
        self.finish_conos['total_cont_conos'] = len(self.extract_conos.get('containers', []))
        
        # 3. Box count (only if EX13_total_items=True)
        if self.check_in_conos.get('EX13_total_items', False):
            self.finish_conos['boxes_conos'] = self.amounts_conos.get('SUM_boxes', 0)
        
        # 4. Average weight per box
        self.finish_conos['gross_perbox_conos'] = self.amounts_conos.get('MID_perbox', 0.0)
        
        # 5. Total weight (only if EX14_total_GCW=True)
        if self.check_in_conos.get('EX14_total_GCW', False):
            self.finish_conos['gross_conos'] = self.amounts_conos.get('AM_total_weight', 0.0)
        
        # 6. Unique fruits (English)
        unique_fruits = set(self.extract_conos.get('fruits', []))
        self.finish_conos['fruit_eng_conos'] = tuple(unique_fruits)
        
        # Add fruit translations
        if unique_fruits:
            # Spanish names
            es_fruits = []
            # Latin names
            la_fruits = []
            
            for fruit in unique_fruits:
                if fruit in FRUIT_TRANSLATIONS:
                    es_fruits.append(FRUIT_TRANSLATIONS[fruit]['es'])
                    la_fruits.append(FRUIT_TRANSLATIONS[fruit]['la'])
                else:
                    es_fruits.append(fruit)  # If no translation, keep original
                    la_fruits.append(fruit)
            
            self.finish_conos['fruit_esp_conos'] = tuple(es_fruits)
            self.finish_conos['fruit_la_conos'] = tuple(la_fruits)
        else:
            self.finish_conos['fruit_esp_conos'] = ()
            self.finish_conos['fruit_la_conos'] = ()
        
        # 7. Unique FRESH values
        self.finish_conos['fresh_conos'] = tuple(set(self.extract_conos.get('fresh', [])))

        # Add date if exists
        if self.extract_conos.get('EX_1_11_SOB_date'):
            try:
                dt = self.data_extractor.parse_custom_date(self.extract_conos['EX_1_11_SOB_date'])
                self.finish_conos['SOB_date'] = dt.strftime("%d.%m.%Y") if dt else 'N/A'
            except:
                self.finish_conos['SOB_date'] = 'N/A'
        
        return self.finish_conos

    def create_finish_phito(self):
        """Create and update global finish_phito dictionary with per-box calculations"""
        self.finish_phito = {}

        # 1. Container processing
        if self.check_in_phito.get('containers_match', False):
            unique_containers = list(set(
                self.extract_phito.get('Containers_PH_1', []) + 
                self.extract_phito.get('Containers_PH_2', [])
            ))
            self.finish_phito['containers_phito'] = tuple(unique_containers)
            self.finish_phito['total_cont_phito'] = len(unique_containers)

        # 2. Box/BOXES processing (should execute first for calculations)
        if self.check_in_phito.get('all_boxes_match', False):
            self.finish_phito['boxes_phito'] = self.extract_phito.get('PH1_Box')

        # 3. Per-box calculations
        if self.check_in_phito.get('check_netto', False) and 'boxes_phito' in self.finish_phito:
            try:
                self.finish_phito['netto_phito'] = self.extract_phito.get('EX_ph1_8_NETTO')
                self.finish_phito['netto_perbox_phito'] = round(
                    float(self.finish_phito['netto_phito']) / float(self.finish_phito['boxes_phito']), 
                    2
                )
            except (ValueError, ZeroDivisionError):
                self.finish_phito['netto_perbox_phito'] = 'N/A'

        if self.check_in_phito.get('check_gross', False) and 'boxes_phito' in self.finish_phito:
            try:
                self.finish_phito['gross_phito'] = self.extract_phito.get('EX_ph1_8_GROSS')
                self.finish_phito['gross_perbox_phito'] = round(
                    float(self.finish_phito['gross_phito']) / float(self.finish_phito['boxes_phito']), 
                    2
                )
            except (ValueError, ZeroDivisionError):
                self.finish_phito['gross_perbox_phito'] = 'N/A'

        # 4. Other data
        if self.check_in_phito.get('numbers_match', False):
            self.finish_phito['NUMBER_PHITO'] = self.extract_phito.get('page1_number')

        if self.check_in_phito.get('check_fruit_es', False):
            es_fruit = self.extract_phito.get('EX_ph1_8_fruta')
            self.finish_phito['fruit_es_phito'] = es_fruit
            
            # Add English fruit name
            if es_fruit:
                eng_fruit = None
                for fruit, translations in FRUIT_TRANSLATIONS.items():
                    if translations['es'].lower() == es_fruit.lower():
                        eng_fruit = fruit
                        break
                self.finish_phito['fruit_eng_phito'] = eng_fruit if eng_fruit else es_fruit
        
        if self.check_in_phito.get('check_fruit_la', False):
            self.finish_phito['fruit_la_phito'] = self.extract_phito.get('EX_ph1_9_fructus')
            
        # Add FRESH if check passed
        if self.check_in_phito.get('check_fresh', False):
            self.finish_phito['fresh_phito'] = 'FRESH'

        # Add date from phytosanitary
        date1 = self.extract_phito.get('EX_1_17_Date_PHITO', '')
        date2 = self.extract_phito.get('EX_2_17_Date_PHITO', '')
        if date1 == date2 and date1:
            dt = self.data_extractor.parse_custom_date(date1)
            self.finish_phito['date_phito'] = dt.strftime("%d.%m.%Y") if dt else 'N/A'
                
        return self.finish_phito

    def post_process_weights(self):
        """Post-processing of weight data"""
        total_containers = len(self.extract_conos['containers'])
        total_weights = len(self.extract_conos['weights'])
        
        # If weight count exceeds containers by 1
        if total_weights == total_containers + 1:
            print("Found total value in weights. Performing correction...")
            self.extract_conos['EX14_total_GCW'] = self.extract_conos['weights'][-1]
            self.extract_conos['weights'] = self.extract_conos['weights'][:-1]
        elif total_weights > total_containers + 1:
            print(f"Warning! Data mismatch: {total_weights} weights for {total_containers} containers")
        else:
            print("Total weight value not found")
