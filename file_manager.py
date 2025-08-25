import os
import json
import shutil
import logging
from typing import Dict

class FileManager:
    def __init__(self):
        self.CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.pdf_processor')
        self.CONFIG_FILE = os.path.join(self.CONFIG_DIR, 'config.json')
        self.OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
        self._ensure_directories_exist()

    def _ensure_directories_exist(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.CONFIG_DIR, exist_ok=True)
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        os.makedirs(os.path.join(self.OUTPUT_DIR, "cropped_blocks"), exist_ok=True)

    def clean_workspace(self) -> None:
        """Clean working directory while preserving visualizations and log"""
        try:
            if os.path.exists(self.OUTPUT_DIR):
                for item in os.listdir(self.OUTPUT_DIR):
                    if item not in ("cropped_blocks", "pdf_processing.log"):
                        path = os.path.join(self.OUTPUT_DIR, item)
                        if os.path.isdir(path):
                            shutil.rmtree(path)
                        else:
                            os.remove(path)
        except Exception as e:
            logging.error(f"Error cleaning working directory: {str(e)}")
            raise

    def load_last_paths(self) -> Dict[str, str]:
        """Load last paths from config file"""
        try:
            with open(self.CONFIG_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'bill_of_lading': '', 'phytosanitary': ''}

    def save_last_paths(self, last_paths: Dict[str, str]) -> None:
        """Save last paths to config file"""
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(last_paths, f)
        except Exception as e:
            logging.error(f"Error saving paths: {str(e)}")
            raise
