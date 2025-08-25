import tkinter as tk
from tkinter import filedialog, messagebox
import ctypes
import os
from typing import List, Optional, Tuple, Dict
import pdfplumber

class UIHandler:
    def __init__(self, file_manager):
        self.file_manager = file_manager

    def flash_window(self, hwnd) -> None:
        """Make window blink in taskbar (Windows only)"""
        try:
            if hasattr(ctypes, 'windll'):
                FLASHW_ALL = 0x00000003
                FLASHW_TIMERNOFG = 0x0000000C
                flash_info = ctypes.wintypes.FLASHWINFO(
                    cbSize=ctypes.sizeof(ctypes.wintypes.FLASHWINFO),
                    hwnd=hwnd,
                    dwFlags=FLASHW_ALL | FLASHW_TIMERNOFG,
                    uCount=5,
                    dwTimeout=0
                )
                ctypes.windll.user32.FlashWindowEx(ctypes.byref(flash_info))
        except Exception as e:
            print(f"Window flash error: {e}")

    def select_file(self, title: str, filetypes: List[Tuple[str, str]], dialog_type: str) -> Optional[str]:
        """Select file via dialog with improved window behavior"""
        root = tk.Tk()
        root.withdraw()
        
        # Set window on top
        root.attributes('-topmost', True)
        
        last_paths = self.file_manager.load_last_paths()
        initial_dir = last_paths.get(dialog_type, '')
        
        # Create temporary dialog window
        dialog_root = tk.Toplevel(root)
        dialog_root.withdraw()
        
        # Show window on top
        dialog_root.attributes('-topmost', True)
        
        # Get HWND for Windows API
        try:
            if hasattr(ctypes, 'windll'):
                hwnd = ctypes.windll.user32.GetParent(dialog_root.winfo_id())
            else:
                hwnd = None
        except:
            hwnd = None
        
        # Check if window active
        def check_focus():
            try:
                if not dialog_root.focus_displayof() and hwnd:
                    self.flash_window(hwnd)
                dialog_root.after(500, check_focus)
            except:
                pass
        
        dialog_root.after(500, check_focus)
        
        file_path = filedialog.askopenfilename(
            parent=dialog_root,
            title=title,
            filetypes=filetypes,
            initialdir=initial_dir
        )
        
        # Destroy temporary windows
        try:
            dialog_root.destroy()
            root.destroy()
        except:
            pass
        
        if file_path:
            last_paths[dialog_type] = os.path.dirname(file_path)
            self.file_manager.save_last_paths(last_paths)
        
        return file_path

    def select_phytosanitary_files(self) -> Optional[List[str]]:
        """Select phytosanitary certificate files with improved UI"""
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        # First window
        first_file = self.select_file(
            "Select phytosanitary certificate",
            [("PDF Files", "*.pdf"), ("All Files", "*.*")],
            'phytosanitary'
        )
        
        if not first_file:
            root.destroy()
            return None
        
        # Analyze orientation
        orientation = None
        with pdfplumber.open(first_file) as pdf:
            if len(pdf.pages) >= 2:
                # Check if both orientations present
                first_vert = pdf.pages[0].height > pdf.pages[0].width
                second_vert = pdf.pages[1].height > pdf.pages[1].width
                
                if first_vert and not second_vert:
                    root.destroy()
                    return [first_file]  # Two-page document
            
            # Determine first page orientation
            orientation = "vertical" if pdf.pages[0].height > pdf.pages[0].width else "horizontal"
        
        # Second window (if needed)
        required_orientation = "horizontal" if orientation == "vertical" else "vertical"
        title = f"Select {'vertical' if required_orientation == 'vertical' else 'horizontal'} phytosanitary"
        
        while True:
            second_file = self.select_file(
                title,
                [("PDF Files", "*.pdf"), ("All Files", "*.*")],
                'phytosanitary'
            )
            
            if not second_file:
                root.destroy()
                return [first_file]
            
            if second_file == first_file:
                messagebox.showerror("Error", "Same file selected! Please select different file.")
                continue
            
            # Check orientation
            with pdfplumber.open(second_file) as pdf:
                page_orientation = "vertical" if pdf.pages[0].height > pdf.pages[0].width else "horizontal"
                
                if page_orientation != required_orientation:
                    messagebox.showerror(
                        "Orientation error",
                        f"Required {required_orientation} page orientation!"
                    )
                    continue
            
            root.destroy()
            return [first_file, second_file]

    @staticmethod
    def show_error_message(title: str, message: str) -> None:
        """Show error message box"""
        messagebox.showerror(title, message)

    @staticmethod
    def show_info_message(title: str, message: str) -> None:
        """Show info message box"""
        messagebox.showinfo(title, message)
