# ================= IMPORTS =================
import re
import logging
import os
import shutil
import pdfplumber
import json
import tkinter as tk
import gc
from datetime import datetime
from tkinter import filedialog
from openpyxl import Workbook
from openpyxl.styles import Alignment, PatternFill, Font, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment
from PIL import Image, ImageDraw, ImageFont
import math
from pdfplumber.page import Page
from PIL.Image import Image as PILImage
from tkinter import Tk, Toplevel
import tkinter.messagebox as messagebox
import ctypes
import time
import importlib
from configs.config_blocks import BASE_BLOCKS, BLOCKS_CONFIG
from configs.config_phytosanitary import PHYTOSANITARY_CONFIG, PHYTO_CONTAINER_PATTERN, PHYTO_VALIDATION_PATTERNS
from configs.config_fruits import FRUITS, FRUIT_TRANSLATIONS
from core.ml_blocks_adapter import extract_blocks_from_pdf_page, extract_ml_title_blocks, extract_ml_rider_blocks

from modules.output_excel import ExcelExporter
from modules.file_manager import FileManager
from modules.ui_handler import UIHandler
from modules.visualization_helper import VisualizationHelper
from modules.data_validator import DataValidator
from modules.data_extractor import DataExtractor
from modules.data_processor import DataProcessor
from modules.document_processor import DocumentProcessor  # <-- NEW

# ================= CONSTANTS =================
EXCEL_PATH = os.path.join(os.path.dirname(__file__), "output", "output.xlsx")

CHARTER_BLOCKS = {
    "CONGENBIAL_1994": {
        "key_phrases": {
            "shipper": ["SHipper", "HORIZON FRESH FRUIT EXPORT"],
            "consignee": ["Consignee", "JSC <<GRAND-TRADE>>"],
            "vessel": ["Vessel", "CROWN OPAL"],
            "goods_table": ["Marks & Nos", "No of pallets", "Gross weight"]
        }
    }
}

class PDFProcessor:
    def __init__(self):
        self.USE_ML = True
        self.file_manager = FileManager()
        self.ui_handler = UIHandler(self.file_manager)
        self.visualizer = VisualizationHelper()
        self.data_extractor = DataExtractor(self)
        
        # Сначала инициализируем DataProcessor
        self.data_processor = DataProcessor(self.data_extractor)
        
        # Теперь можно инициализировать DataValidator
        self.validator = DataValidator(self, self.data_processor)

        # DocumentProcessor — новая прослойка
        self.document_processor = DocumentProcessor(self)
        
        # Инициализируем глобальные переменные
        self.data_processor.init_global_variables()

    def main(self):
        """Main program execution function"""
        # 1. Clean workspace before logging init!
        self.file_manager.clean_workspace()
        
        # 2. Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join("output", "pdf_processing.log")),
                logging.StreamHandler()
            ]
        )

        try:
            # 1. Initialize global variables
            self.data_processor.init_global_variables()
            
            # 2. Select and process bill of lading
            bill_of_lading_path = self.ui_handler.select_file(
                "Select bill of lading file",
                [("PDF Files", "*.pdf"), ("All Files", "*.*")],
                'bill_of_lading'
            )
            
            if not bill_of_lading_path:
                print("Bill of lading file not selected. Program terminated.")
                return
            
            print(f"\nProcessing file: {bill_of_lading_path}")
            self.document_processor.process_pdf(bill_of_lading_path)
            
            # 3. Select and process phytosanitary certificate
            phytosanitary_paths = self.ui_handler.select_phytosanitary_files()
            
            if phytosanitary_paths:
                for path in phytosanitary_paths:
                    self.document_processor.process_phytosanitary(path)
                    self.data_extractor.extract_phytosanitary_values()
            
            # 4. Perform control checks
            self.validator.check_phytosanitary_control()
            self.data_processor.control_results = self.validator.perform_control_checks()
            
            # 5. Create aggregated data
            self.data_processor.create_finish_conos()  # Create finish_conos before comparison
            self.data_processor.create_finish_phito()
            
            # 6. Compare bill of lading and phytosanitary data
            self.validator.compare_conos_phito()
            
            # 7. Export to Excel
            exporter = ExcelExporter(self.data_processor, EXCEL_PATH)
            exporter.export_to_excel()
            saved_path = EXCEL_PATH  # export_to_excel не возвращает путь
            
            # 8. Output debug info
            print("\nProcessing completed successfully!")
            print(f"Results saved to: {saved_path}")
            self.document_processor.print_debug_info()
            
        except Exception as e:
            print(f"\n!!! EXECUTION ERROR !!!")
            print(f"Error type: {type(e).__name__}")
            print(f"Message: {str(e)}")
            logging.exception("Error occurred:")
            
        finally:
            input("\nPress Enter to exit...")

if __name__ == "__main__":
    processor = PDFProcessor()
    processor.main()
