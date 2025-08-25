# modules/visualization_helper.py
import os
import logging
from typing import Tuple, Dict, Any
from pdfplumber.page import Page
from PIL import Image, ImageDraw, ImageFont

class VisualizationHelper:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def calculate_pdf_coordinates(self, page: Page, config: Dict[str, float]) -> Tuple[float, float, float, float]:
        """Calculate coordinates for PDF page based on percentage values"""
        return (
            page.width * config['left_pct'] / 100,
            page.height * config['top_pct'] / 100,
            page.width * config['right_pct'] / 100,
            page.height * config['bottom_pct'] / 100
        )

    def visualize_block(self, page: Page, config: Dict[str, Any], block_type: str) -> str:
        """Visualize a block from PDF with red border and label"""
        try:
            # Create subdirectory for cropped blocks
            output_dir = os.path.join(self.output_dir, "cropped_blocks")
            os.makedirs(output_dir, exist_ok=True)
            
            filename = f"{block_type}_block_{config['num']}_page_{config['page']}.png"
            output_path = os.path.join(output_dir, filename)
            
            # Get coordinates and convert to image space
            coords = self.calculate_pdf_coordinates(page, config)
            img = self._create_block_image(page, coords, config, block_type)
            img.save(output_path)
            
            return output_path
        except Exception as e:
            logging.error(f"Visualization error: {str(e)}")
            return ""

    def visualize_phytosanitary_block(self, page: Page, block_config: Dict[str, Any], 
                                    orientation: str, page_num: int) -> str:
        """Visualize phytosanitary certificate block with labeling"""
        try:
            output_dir = os.path.join(self.output_dir, "phytosanitary_blocks")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"phyto_p{page_num}_b{block_config['num']}.png")

            # Calculate coordinates
            left = page.width * block_config['left_pct'] / 100
            top = page.height * block_config['top_pct'] / 100
            right = page.width * block_config['right_pct'] / 100
            bottom = page.height * block_config['bottom_pct'] / 100

            # Create and save image
            img = self._create_block_image(
                page, 
                (left, top, right, bottom),
                block_config,
                f"Phyto {orientation}"
            )
            img.save(output_path)
            return output_path
        except Exception as e:
            logging.error(f"Phyto visualization error: {str(e)}")
            return ""

    def _create_block_image(self, page: Page, coords: Tuple[float, float, float, float], 
                          config: Dict[str, Any], label: str) -> Image.Image:
        """Internal method to create annotated block image"""
        img = page.to_image(resolution=150).original
        draw = ImageDraw.Draw(img)
        
        # Convert coordinates to image space
        x0, y0, x1, y1 = self._convert_coordinates_to_image(img, page, coords)
        
        # Draw rectangle and label
        draw.rectangle([x0, y0, x1, y1], outline="red", width=3)
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        text = f"{config.get('name', '')}\n({label})"
        draw.text((x0 + 5, y0 + 5), text, font=font, fill="red")
        
        return img.crop((x0, y0, x1, y1))

    def _convert_coordinates_to_image(self, img: Image.Image, page: Page, 
                                    coords: Tuple[float, float, float, float]) -> Tuple[int, int, int, int]:
        """Convert PDF coordinates to image pixel coordinates"""
        img_width, img_height = img.size
        scale_x = img_width / page.width
        scale_y = img_height / page.height
        
        x0 = int(coords[0] * scale_x)
        y0 = int(coords[1] * scale_y)
        x1 = int(coords[2] * scale_x)
        y1 = int(coords[3] * scale_y)
        
        # Ensure y0 is top and y1 is bottom
        if y1 < y0:
            y0, y1 = y1, y0
            
        return x0, y0, x1, y1
