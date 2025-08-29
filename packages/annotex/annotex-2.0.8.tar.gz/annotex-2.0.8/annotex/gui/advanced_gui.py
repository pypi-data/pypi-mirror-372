#!/usr/bin/env python3
"""
Annotex
Professional-grade annotation with all manual and automated features
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, colorchooser, simpledialog
from pathlib import Path
import json
import cv2
import numpy as np
import threading
import time
from datetime import datetime
import math
import os
import shutil
import yaml
import random
# from annotex.core.annotation_engine import AnnotationEngine
# from annotex.core.dataset_manager import DatasetManager
import sys
import webbrowser

# PIL for image handling
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available. Install with: pip install Pillow")


# Fallback classes for missing modules
class AnnotationEngine:
    def __init__(self):
        self.model = None
        self.class_names = []
        self.confidence_threshold = 0.5
        
    def load_model(self, path):
        """Load YOLO model with better error handling"""
        try:
            model_path = Path(path)
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {path}")
                
            # Check file size
            file_size = model_path.stat().st_size
            if file_size == 0:
                raise ValueError("Model file is empty")
                
            # Try to import ultralytics YOLO
            try:
                from ultralytics import YOLO
                self.model = YOLO(str(model_path))
                
                # Get class names from model
                if hasattr(self.model, 'names'):
                    self.class_names = list(self.model.names.values())
                else:
                    self.class_names = [f"class_{i}" for i in range(80)]  # COCO default
                    
                print(f"✅ YOLO model loaded: {model_path.name}")
                print(f"📋 Classes: {len(self.class_names)}")
                return True
                
            except ImportError:
                raise ImportError("ultralytics not installed. Run: pip install ultralytics")
            except Exception as model_error:
                raise Exception(f"Failed to load YOLO model: {model_error}")
                        
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            self.model = None
            self.class_names = []
            return False
            
    def predict(self, image_path, conf_threshold=None):
        """Run inference on image"""
        if self.model is None:
            return []
            
        if conf_threshold is None:
            conf_threshold = self.confidence_threshold
            
        try:
            # For ultralytics YOLO
            if hasattr(self.model, 'predict'):
                results = self.model.predict(str(image_path), conf=conf_threshold, verbose=False)
                return self.parse_ultralytics_results(results)
            else:
                # For OpenCV DNN (simplified)
                return []
                
        except Exception as e:
            print(f"❌ Prediction failed: {e}")
            return []
            
    def parse_ultralytics_results(self, results):
        """Parse ultralytics YOLO results"""
        detections = []
        
        for result in results:
            if result.boxes is not None:
                boxes = result.boxes.xyxy.cpu().numpy()  # x1, y1, x2, y2
                confidences = result.boxes.conf.cpu().numpy()
                classes = result.boxes.cls.cpu().numpy().astype(int)
                
                for box, conf, cls in zip(boxes, confidences, classes):
                    x1, y1, x2, y2 = box
                    detection = {
                        'class_id': int(cls),
                        'class_name': self.class_names[cls] if cls < len(self.class_names) else f"class_{cls}",
                        'confidence': float(conf),
                        'bbox': [float(x1), float(y1), float(x2), float(y2)]  # x1, y1, x2, y2
                    }
                    detections.append(detection)
                    
        return detections
        
    def set_confidence_threshold(self, thresh):
        self.confidence_threshold = thresh

class DatasetManager:
    def __init__(self): 
        pass
        
    def create_yolo_dataset(self, *args, **kwargs):
        return False

class Annotex:
    """Annotex"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Annotex v2.1")
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate proportional window size (95% of screen)
        window_width = int(screen_width * 0.95)
        window_height = int(screen_height * 0.90)
        
        # Ensure minimum size
        window_width = max(1200, window_width)
        window_height = max(700, window_height)
        
        # Center window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(True, True)
        
        # Calculate scale factor for proportional resizing
        self.scale_factor = min(window_width / 1600, window_height / 1000)
        
        # Continue with ALL your existing initialization
        self.engine = AnnotationEngine()
        self.manager = DatasetManager()
        
        self.current_image = None
        self.current_image_path = None
        self.original_image = None
        self.image_list = []
        self.current_image_index = 0
        self.current_annotations = []
        self.selected_annotation = None
        
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.canvas_width = 0
        self.canvas_height = 0
        
        self.annotation_mode = "rectangle"
        self.is_drawing = False
        self.is_panning = False
        self.current_polygon_points = []
        self.temp_line_id = None
        
        self.start_x = 0
        self.start_y = 0
        self.last_x = 0
        self.last_y = 0
        self.current_bbox = None
        self.resize_handle = None
        self.resize_anchor = None
        
        self.classes = []
        self.selected_class_id = 0
        self.next_class_id = 0
        
        self.confidence_threshold = 0.5
        self.auto_save = True
        self.brush_size = 3
        self.show_labels = True
        self.show_confidence = True
        
        self.train_split = 0.8
        self.val_split = 0.2
        self.export_format = "YOLO11"
        
        self.copied_annotation = None
        
        self.create_gui()
        self.setup_bindings()
        
        self.update_status("Ready - Load images to start annotation")
        self.log_message("🚀 Annotex!")
        self.log_message(f"PIL Available: {PIL_AVAILABLE}")
        self.check_dependencies()

    # Annotex class
    def fix_class_ids(self):
        """Fix class IDs to start from 0 (YOLO requirement)"""
        if not self.classes:
            return
            
        # Reindex all classes to start from 0
        old_to_new = {}
        for i, class_info in enumerate(self.classes):
            old_id = class_info['id']
            class_info['id'] = i
            old_to_new[old_id] = i
            
        # Update next_class_id
        self.next_class_id = len(self.classes)
        
        # Update current annotations
        for ann in self.current_annotations:
            if ann['class_id'] in old_to_new:
                ann['class_id'] = old_to_new[ann['class_id']]
        
        self.update_class_list()
        self.display_image()
        self.log_message(f"Fixed class IDs: {old_to_new}")

    def load_project_file(self, file_path):
        """Load project from command line"""
        try:
            with open(file_path, 'r') as f:
                project_data = json.load(f)
                
            # Reuse your existing load_project logic
            self.image_list = [Path(img_path) for img_path in project_data["image_list"]]
            self.classes = project_data["classes"]
            self.selected_class_id = project_data.get("selected_class_id", 0)
            
            # Update UI
            self.update_image_listbox()
            self.update_class_list()
            if self.image_list:
                self.current_image_index = 0
                self.load_current_image()
                
            self.log_message(f"✅ Loaded project: {Path(file_path).name}")
            
        except Exception as e:
            self.log_message(f"❌ Error loading project: {e}")

    def load_images_from_path(self, images_path):
        """Load images from command line path"""
        try:
            directory = Path(images_path)
            if not directory.exists():
                self.log_message(f"❌ Directory not found: {images_path}")
                return
                
            # Reuse your existing load_images logic
            image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp')
            self.image_list = []
            
            for ext in image_extensions:
                self.image_list.extend(directory.glob(f"*{ext}"))
                self.image_list.extend(directory.glob(f"*{ext.upper()}"))
            
            self.image_list = sorted(list(set(self.image_list)))
            
            if self.image_list:
                self.update_image_listbox()
                self.current_image_index = 0
                self.load_current_image()
                self.log_message(f"✅ Loaded {len(self.image_list)} images")
            else:
                self.log_message(f"❌ No images found in {directory}")
                
        except Exception as e:
            self.log_message(f"❌ Error loading images: {e}")
    
    def check_dependencies(self):
        """Check for optional dependencies"""
        try:
            from ultralytics import YOLO
            self.yolo_available = True
            self.log_message("✅ YOLO available")
        except ImportError:
            self.yolo_available = False
            self.log_message("⚠️ YOLO not available. Install with: pip install ultralytics")
            
        try:
            import yaml
            self.yaml_available = True
        except ImportError:
            self.yaml_available = False
            self.log_message("⚠️ YAML not available. Install with: pip install pyyaml")

    def create_gui(self):
        """Create the complete GUI"""
        self.create_main_frames()
        self.create_left_panel()      
        self.create_center_panel()
        self.create_right_panel()       
        self.create_bottom_panel()
        self.create_status_bar()
        self.create_menus()
            
    def create_main_frames(self):
        """Create main frame structure with proportional sizing"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='both', expand=True)
        
        # Scale panel sizes proportionally based on screen size
        left_width = int(350 * self.scale_factor)
        # INCREASED: Right panel width to accommodate longer button text
        right_width = int(380 * self.scale_factor) 
        bottom_height = int(120 * self.scale_factor)
        
        # Ensure minimum usable sizes - INCREASED minimum for right panel
        left_width = max(250, left_width)
        right_width = max(280, right_width) 
        bottom_height = max(80, bottom_height)
        
        # Left panel - Tools & Classes
        self.left_frame = ttk.LabelFrame(top_frame, text="Tools & Classes", width=left_width)
        self.left_frame.pack(side='left', fill='y', padx=(0,5))
        self.left_frame.pack_propagate(False)
        
        # Center panel - Image viewer
        self.center_frame = ttk.LabelFrame(top_frame, text="Image Viewer")
        self.center_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Right panel - Images & Export
        self.right_frame = ttk.LabelFrame(top_frame, text="Images & Export", width=right_width)
        self.right_frame.pack(side='right', fill='y', padx=(5,0))
        self.right_frame.pack_propagate(False)
        
        # Bottom panel - Console
        self.bottom_frame = ttk.LabelFrame(main_frame, text="Console & Status", height=bottom_height)
        self.bottom_frame.pack(fill='x', pady=(5,0))
        self.bottom_frame.pack_propagate(False)
        
    def create_left_panel(self):
        """Create left panel with adaptive content sizing"""
        # Manual Annotation Tools
        manual_frame = ttk.LabelFrame(self.left_frame, text="🔲 Manual Annotation Tools")
        manual_frame.pack(fill='x', padx=3, pady=3)
        
        # Annotation tools
        tools_frame = ttk.Frame(manual_frame)
        tools_frame.pack(fill='x', padx=3, pady=3)
        
        self.tool_buttons = {}
        tools = [
            ("🔲 Rectangle", "rectangle"),
            ("🔷 Polygon", "polygon"), 
            ("📍 Point", "point"),
            ("🖌️ Brush", "brush")
        ]
        
        # Adaptive button width
        btn_width = max(12, min(15, int(15 * self.scale_factor)))
        
        for i, (text, mode) in enumerate(tools):
            if mode == "rectangle":
                btn = tk.Button(tools_frame, text=text, 
                            command=lambda m=mode: self.set_annotation_mode(m),
                            width=btn_width, relief='raised')
            else:
                btn = tk.Button(tools_frame, text=text, 
                            command=lambda m=mode: self.show_coming_soon(m),
                            width=btn_width, relief='raised',
                            bg='#E0E0E0', fg='#888888', state='normal')
            
            btn.grid(row=i//2, column=i%2, padx=1, pady=1, sticky='ew')
            self.tool_buttons[mode] = btn
            
        tools_frame.columnconfigure(0, weight=1)
        tools_frame.columnconfigure(1, weight=1)
        
        self.set_annotation_mode("rectangle")
        
        # Edit tools
        edit_frame = ttk.LabelFrame(self.left_frame, text="Edit Tools")
        edit_frame.pack(fill='x', padx=3, pady=3)
        
        edit_buttons = [
            ("✏️ Edit", self.edit_selected),
            ("🗑 Delete", self.delete_selected),
            ("📋 Copy", self.copy_selected),
            ("📄 Paste", self.paste_annotation),
            ("↩️ Undo", self.undo_action),
            ("🔄 Clear All", self.clear_all_annotations)
        ]
        
        for i, (text, command) in enumerate(edit_buttons):
            btn = ttk.Button(edit_frame, text=text, command=command, width=btn_width)
            btn.grid(row=i//2, column=i%2, padx=1, pady=1, sticky='ew')
            
        edit_frame.columnconfigure(0, weight=1)
        edit_frame.columnconfigure(1, weight=1)
        
        # Class Management
        class_frame = ttk.LabelFrame(self.left_frame, text="🏷️ Class Management")
        class_frame.pack(fill='x', padx=3, pady=3)
        
        # Current selected class display
        current_class_frame = ttk.Frame(class_frame)
        current_class_frame.pack(fill='x', padx=3, pady=2)
        
        ttk.Label(current_class_frame, text="Selected:").pack(side='left')
        self.current_class_label = ttk.Label(current_class_frame, text="No Classes", 
                                        background='lightgray', width=12)
        self.current_class_label.pack(side='right')
        
        # Class list
        list_frame = ttk.Frame(class_frame)
        list_frame.pack(fill='x', padx=3, pady=2)
        
        # Calculate adaptive height based on screen size with proper bounds
        # Small screens: 3-4 lines, Medium: 4-6 lines, Large: 6-12 lines
        screen_height = self.root.winfo_screenheight()
        if screen_height <= 768:  # Small screens (laptops)
            list_height = 3
        elif screen_height <= 1080:  # Medium screens
            list_height = max(4, min(6, int(6 * self.scale_factor)))
        else:  # Large screens
            list_height = max(6, min(12, int(8 * self.scale_factor)))
        
        self.class_listbox = tk.Listbox(list_frame, height=list_height, selectmode='single')
        class_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', 
                                    command=self.class_listbox.yview)
        self.class_listbox.configure(yscrollcommand=class_scrollbar.set)
        
        self.class_listbox.pack(side='left', fill='both', expand=True)
        class_scrollbar.pack(side='right', fill='y')
        
        self.class_listbox.bind('<<ListboxSelect>>', self.on_class_select)
        self.class_listbox.bind('<Double-Button-1>', self.edit_class)
        
        # Class management buttons (compact, at bottom)
        class_btn_frame = ttk.Frame(class_frame)
        class_btn_frame.pack(fill='x', padx=3, pady=2)
        
        compact_btn_width = max(8, min(12, int(8 * self.scale_factor)))
        
        ttk.Button(class_btn_frame, text="➕", 
                command=self.add_class_dialog, width=4).pack(side='left', padx=1)
        ttk.Button(class_btn_frame, text="✏️", 
                command=self.edit_class, width=4).pack(side='left', padx=1)
        ttk.Button(class_btn_frame, text="🗑", 
                command=self.delete_class, width=4).pack(side='left', padx=1)
        
        self.update_class_list()
        
        # Semi-Automated Tools 
        auto_frame = ttk.LabelFrame(self.left_frame, text="🤖 AI Tools")
        auto_frame.pack(fill='x', padx=3, pady=3)
        
        # Model loading 
        model_frame = ttk.Frame(auto_frame)
        model_frame.pack(fill='x', padx=3, pady=2)
        
        ttk.Label(model_frame, text="Model:").pack(anchor='w')
        
        model_entry_frame = ttk.Frame(model_frame)
        model_entry_frame.pack(fill='x', pady=1)
        
        self.model_path_var = tk.StringVar()
        model_entry = ttk.Entry(model_entry_frame, textvariable=self.model_path_var, width=15)
        model_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(model_entry_frame, text="📂", command=self.browse_model, width=3).pack(side='right')
        
        ttk.Button(model_frame, text="🔄 Load Model", command=self.load_model, 
                width=btn_width).pack(fill='x', pady=1)
        
        # Confidence settings 
        conf_frame = ttk.Frame(auto_frame)
        conf_frame.pack(fill='x', padx=3, pady=2)
        
        ttk.Label(conf_frame, text="Confidence:").pack(anchor='w')
        self.conf_var = tk.DoubleVar(value=self.confidence_threshold)
        conf_scale = ttk.Scale(conf_frame, from_=0.1, to=1.0, 
                            variable=self.conf_var, orient='horizontal',
                            command=self.update_confidence)
        conf_scale.pack(fill='x', padx=2)
        
        self.conf_label = ttk.Label(conf_frame, text=f"{self.confidence_threshold:.2f}")
        self.conf_label.pack()
        
        # Auto-annotation buttons
        auto_btn_frame = ttk.Frame(auto_frame)
        auto_btn_frame.pack(fill='x', padx=3, pady=2)
        
        ttk.Button(auto_btn_frame, text="🎯 Auto-Annotate Current", 
                command=self.auto_annotate_current, width=btn_width).pack(fill='x', pady=1)
        ttk.Button(auto_btn_frame, text="📋 Auto-Annotate All", 
                command=self.auto_annotate_all, width=btn_width).pack(fill='x', pady=1)
        ttk.Button(auto_btn_frame, text="💡 Suggestions", 
                command=self.smart_suggestions, width=btn_width).pack(fill='x', pady=1)
        
    def create_manual_annotation_section(self, parent):
        """Create manual annotation tools section"""
        manual_frame = ttk.LabelFrame(parent, text="📝 Manual Annotation Tools")
        manual_frame.pack(fill='x', padx=5, pady=5)
        
        # Annotation tools
        tools_frame = ttk.Frame(manual_frame)
        tools_frame.pack(fill='x', padx=5, pady=5)
        
        self.tool_buttons = {}
        tools = [
            ("🔲 Rectangle", "rectangle"),
            ("🔷 Polygon", "polygon"), 
            ("📍 Point", "point"),
            ("🖌️ Brush", "brush")
        ]
        
        for i, (text, mode) in enumerate(tools):
            if mode == "rectangle":
                # Active tool
                btn = tk.Button(tools_frame, text=text, 
                            command=lambda m=mode: self.set_annotation_mode(m),
                            width=15, relief='raised')
            else:
                # Disabled tools
                btn = tk.Button(tools_frame, text=text, 
                            command=lambda m=mode: self.show_coming_soon(m),
                            width=15, relief='raised',
                            bg='#E0E0E0', fg='#888888', state='normal')
            
            btn.grid(row=i//2, column=i%2, padx=2, pady=2, sticky='ew')
            self.tool_buttons[mode] = btn
            
        tools_frame.columnconfigure(0, weight=1)
        tools_frame.columnconfigure(1, weight=1)
        
        # Set default mode
        self.set_annotation_mode("rectangle")
        
        # Edit tools (keep as before)
        edit_frame = ttk.LabelFrame(manual_frame, text="Edit Tools")
        edit_frame.pack(fill='x', padx=5, pady=5)
        
        edit_buttons = [
            ("✏️ Edit", self.edit_selected),
            ("🗑 Delete", self.delete_selected),
            ("📋 Copy", self.copy_selected),
            ("📄 Paste", self.paste_annotation),
            ("↩️ Undo", self.undo_action),
            ("🔄 Clear All", self.clear_all_annotations)
        ]
        
        for i, (text, command) in enumerate(edit_buttons):
            btn = ttk.Button(edit_frame, text=text, command=command, width=18)
            btn.grid(row=i//2, column=i%2, padx=1, pady=1, sticky='ew')
            
        edit_frame.columnconfigure(0, weight=1)
        edit_frame.columnconfigure(1, weight=1)

    # ==================== Coming Soon Handler ====================

    def show_coming_soon(self, tool_name):
        """Show minimal coming soon dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Coming Soon!")
        dialog.geometry("300x280")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 150, self.root.winfo_rooty() + 150))
        
        # Icon and title only
        ttk.Label(dialog, text="🚀", font=("Arial", 48)).pack(pady=20)
        ttk.Label(dialog, text="Coming Soon!", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Close button
        ttk.Button(dialog, text="OK", command=dialog.destroy, width=15).pack(pady=20)
        
        self.log_message(f"ℹ️ {tool_name.title()} tool - Coming soon")

        
    def create_class_management_section(self, parent):
        """Create dynamic class management section"""
        class_frame = ttk.LabelFrame(parent, text="🏷️ Class Management")
        class_frame.pack(fill='x', padx=5, pady=5)
        
        # Current selected class display
        current_class_frame = ttk.Frame(class_frame)
        current_class_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(current_class_frame, text="Selected Class:").pack(side='left')
        self.current_class_label = ttk.Label(current_class_frame, text="None", 
                                           background='lightgray', width=15)
        self.current_class_label.pack(side='right')
        
        # Class list with colors
        list_frame = ttk.Frame(class_frame)
        list_frame.pack(fill='both', expand=True, padx=5, pady=2)
        
        self.class_listbox = tk.Listbox(list_frame, height=6, selectmode='single')
        class_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', 
                                       command=self.class_listbox.yview)
        self.class_listbox.configure(yscrollcommand=class_scrollbar.set)
        
        self.class_listbox.pack(side='left', fill='both', expand=True)
        class_scrollbar.pack(side='right', fill='y')
        
        self.class_listbox.bind('<<ListboxSelect>>', self.on_class_select)
        self.class_listbox.bind('<Double-Button-1>', self.edit_class)
        
        # Class management buttons
        class_btn_frame = ttk.Frame(class_frame)
        class_btn_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Button(class_btn_frame, text="➕ Add Class", 
                  command=self.add_class_dialog, width=12).pack(side='left', padx=1)
        ttk.Button(class_btn_frame, text="✏️ Edit", 
                  command=self.edit_class, width=8).pack(side='left', padx=1)
        ttk.Button(class_btn_frame, text="🗑 Delete", 
                  command=self.delete_class, width=8).pack(side='left', padx=1)
        
        # Update class list display
        self.update_class_list()
        
    def create_semi_automated_section(self, parent):
        """Create semi-automated annotation section"""
        auto_frame = ttk.LabelFrame(parent, text="🤖 Semi-Automated Tools")
        auto_frame.pack(fill='x', padx=5, pady=5)
        
        # Model loading
        model_frame = ttk.Frame(auto_frame)
        model_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(model_frame, text="Model File:").pack(anchor='w')
        
        model_entry_frame = ttk.Frame(model_frame)
        model_entry_frame.pack(fill='x', pady=2)
        
        self.model_path_var = tk.StringVar()
        ttk.Entry(model_entry_frame, textvariable=self.model_path_var, width=25).pack(side='left', fill='x', expand=True)
        ttk.Button(model_entry_frame, text="📂", command=self.browse_model, width=3).pack(side='right')
        
        ttk.Button(model_frame, text="🔄 Load Model", command=self.load_model).pack(fill='x', pady=2)
        
        # Confidence settings
        conf_frame = ttk.Frame(auto_frame)
        conf_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(conf_frame, text="Confidence Threshold:").pack(anchor='w')
        self.conf_var = tk.DoubleVar(value=self.confidence_threshold)
        conf_scale = ttk.Scale(conf_frame, from_=0.1, to=1.0, 
                              variable=self.conf_var, orient='horizontal',
                              command=self.update_confidence)
        conf_scale.pack(fill='x', padx=5)
        
        self.conf_label = ttk.Label(conf_frame, text=f"{self.confidence_threshold:.2f}")
        self.conf_label.pack()
        
        # Auto-annotation buttons
        auto_btn_frame = ttk.Frame(auto_frame)
        auto_btn_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Button(auto_btn_frame, text="🎯 Auto-Annotate Current", 
                  command=self.auto_annotate_current).pack(fill='x', pady=1)
        ttk.Button(auto_btn_frame, text="📁 Auto-Annotate All", 
                  command=self.auto_annotate_all).pack(fill='x', pady=1)
        ttk.Button(auto_btn_frame, text="🔍 Smart Suggestions", 
                  command=self.smart_suggestions).pack(fill='x', pady=1)
        
    def create_center_panel(self):
        """Create center image display panel"""
        # Toolbar
        toolbar = ttk.Frame(self.center_frame)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        # Left toolbar - Navigation
        nav_frame = ttk.Frame(toolbar)
        nav_frame.pack(side='left')
        
        # ttk.Button(nav_frame, text="⏮️", command=self.first_image, width=3).pack(side='left', padx=1)
        # ttk.Button(nav_frame, text="⏪", command=self.prev_image, width=3).pack(side='left', padx=1)
        # ttk.Button(nav_frame, text="⏩", command=self.next_image, width=3).pack(side='left', padx=1)
        # ttk.Button(nav_frame, text="⏭️", command=self.last_image, width=3).pack(side='left', padx=1)


        # Create navigation buttons and store references for tooltips
        first_btn = ttk.Button(nav_frame, text="⏮️", command=self.first_image, width=3)
        first_btn.pack(side='left', padx=1)

        prev_btn = ttk.Button(nav_frame, text="⏪", command=self.prev_image, width=3)
        prev_btn.pack(side='left', padx=1)

        next_btn = ttk.Button(nav_frame, text="⏩", command=self.next_image, width=3)
        next_btn.pack(side='left', padx=1)

        last_btn = ttk.Button(nav_frame, text="⏭️", command=self.last_image, width=3)
        last_btn.pack(side='left', padx=1)

        self.create_tooltip(first_btn, "First Image")
        self.create_tooltip(prev_btn, "Previous Image")
        self.create_tooltip(next_btn, "Next Image")
        self.create_tooltip(last_btn, "Last Image")

        # Image counter
        self.image_counter = ttk.Label(nav_frame, text="0/0", font=('Arial', 10, 'bold'))
        self.image_counter.pack(side='left', padx=10)
        
        # Center toolbar - View controls
        view_frame = ttk.Frame(toolbar)
        view_frame.pack(side='left', padx=20)
        
        # ttk.Button(view_frame, text="🔍+", command=self.zoom_in, width=4).pack(side='left', padx=1)
        # ttk.Button(view_frame, text="🔍-", command=self.zoom_out, width=4).pack(side='left', padx=1)
        # ttk.Button(view_frame, text="🔍↻", command=self.zoom_fit, width=4).pack(side='left', padx=1)
        # ttk.Button(view_frame, text="↻", command=self.reset_view, width=3).pack(side='left', padx=1)

        # Create buttons and store references if you want tooltips later
        zoom_in_btn = ttk.Button(view_frame, text="🔍+", command=self.zoom_in, width=4)
        zoom_in_btn.pack(side='left', padx=1)
        
        zoom_out_btn = ttk.Button(view_frame, text="🔍-", command=self.zoom_out, width=4)
        zoom_out_btn.pack(side='left', padx=1)
        
        zoom_fit_btn = ttk.Button(view_frame, text="🔍↻", command=self.zoom_fit, width=4)
        zoom_fit_btn.pack(side='left', padx=1)
        
        reset_btn = ttk.Button(view_frame, text="↻", command=self.reset_view, width=3)
        reset_btn.pack(side='left', padx=1)

        self.create_tooltip(zoom_in_btn, "Zoom In")
        self.create_tooltip(zoom_out_btn, "Zoom Out")
        self.create_tooltip(zoom_fit_btn, "Fit to Screen")
        self.create_tooltip(reset_btn, "Reset View")
        
        self.zoom_label = ttk.Label(view_frame, text="100%", width=6)
        self.zoom_label.pack(side='left', padx=5)

        # Mode and cursor indicators
        self.mode_label = ttk.Label(view_frame, text="Mode: Rectangle", width=15)
        self.mode_label.pack(side='left', padx=5)

        self.cursor_label = ttk.Label(view_frame, text="🖱️", width=3)
        self.cursor_label.pack(side='left', padx=2)
        
        # Right toolbar - Display options
        display_frame = ttk.Frame(toolbar)
        display_frame.pack(side='right')
        
        self.show_labels_var = tk.BooleanVar(value=self.show_labels)
        ttk.Checkbutton(display_frame, text="Labels", 
                       variable=self.show_labels_var,
                       command=self.toggle_labels).pack(side='left', padx=2)
        
        self.show_conf_var = tk.BooleanVar(value=self.show_confidence)
        ttk.Checkbutton(display_frame, text="Confidence", 
                       variable=self.show_conf_var,
                       command=self.display_image).pack(side='left', padx=2)
        
        # Canvas with scrollbars
        canvas_frame = ttk.Frame(self.center_frame)
        canvas_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create canvas with scrollbars
        self.canvas = tk.Canvas(canvas_frame, bg='#2a2a2a', highlightthickness=1,
                               highlightbackground='#555555')
        
        self.h_scrollbar = ttk.Scrollbar(canvas_frame, orient='horizontal', command=self.canvas.xview)
        self.v_scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        
        # Grid layout for canvas and scrollbars
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.h_scrollbar.grid(row=1, column=0, sticky='ew')
        self.v_scrollbar.grid(row=0, column=1, sticky='ns')
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Store canvas dimensions
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
    def create_right_panel(self):
        """Create right panel with adaptive content sizing"""
        # Image management
        img_frame = ttk.LabelFrame(self.right_frame, text="📁 Image Management")
        img_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # IMPROVED: Better button width calculation for wider panel
        # Base button width on actual panel width rather than arbitrary scaling
        button_width = max(25, min(30, int(28 * self.scale_factor))) 
        
        ttk.Button(img_frame, text="📂 Load Images Folder", 
                command=self.load_images, width=button_width).pack(pady=3)
        
        ttk.Button(img_frame, text="📄 Add Individual Images", 
                command=self.add_individual_images, width=button_width).pack(pady=2)
        
        # Image list with adaptive height
        list_height = max(6, min(12, int(12 * self.scale_factor)))
        
        list_container = ttk.Frame(img_frame)
        list_container.pack(fill='both', expand=True, pady=3)
        
        self.image_listbox = tk.Listbox(list_container, height=list_height)
        img_scrollbar = ttk.Scrollbar(list_container, orient='vertical', 
                                    command=self.image_listbox.yview)
        self.image_listbox.configure(yscrollcommand=img_scrollbar.set)
        
        self.image_listbox.pack(side='left', fill='both', expand=True)
        img_scrollbar.pack(side='right', fill='y')
        
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)

        # Image management buttons 
        img_btn_frame = ttk.Frame(img_frame)
        img_btn_frame.pack(fill='x', pady=2)
        
        # Better button width for management buttons
        mgmt_btn_width = max(11, min(15, int(14 * self.scale_factor)))
        
        ttk.Button(img_btn_frame, text="🗑 Remove", 
                command=self.remove_selected_image, width=mgmt_btn_width).pack(side='left', padx=2)
        ttk.Button(img_btn_frame, text="🧹 Clear All", 
                command=self.clear_all_images, width=mgmt_btn_width).pack(side='right', padx=2)
        
        # Image info
        self.image_info_label = ttk.Label(img_frame, text="No image loaded", 
                                        background='lightgray', width=button_width, anchor='center')
        self.image_info_label.pack(pady=2)
        
        # Export section
        export_frame = ttk.LabelFrame(self.right_frame, text="📤 Export Dataset")
        export_frame.pack(fill='x', padx=5, pady=3)
        
        # Format selection
        format_frame = ttk.Frame(export_frame)
        format_frame.pack(fill='x', padx=3, pady=2)
        
        ttk.Label(format_frame, text="Format:").pack(side='left')
        self.export_format_var = tk.StringVar(value="YOLO11")
        # Better combo width for wider panel
        combo_width = max(10, min(15, int(14 * self.scale_factor)))
        format_combo = ttk.Combobox(format_frame, textvariable=self.export_format_var,
                                values=["YOLO11", "YOLOv8"],
                                state='readonly', width=combo_width)
        format_combo.pack(side='right')
        
        # Split ratios
        split_frame = ttk.LabelFrame(export_frame, text="Dataset Split")
        split_frame.pack(fill='x', padx=3, pady=2)
        
        # Train split
        train_frame = ttk.Frame(split_frame)
        train_frame.pack(fill='x', pady=1)
        ttk.Label(train_frame, text="Train:").pack(side='left')
        self.train_var = tk.DoubleVar(value=0.8)
        train_scale = ttk.Scale(train_frame, from_=0.5, to=0.9, 
                            variable=self.train_var, orient='horizontal',
                            command=self.update_split_ratios)
        train_scale.pack(side='left', fill='x', expand=True, padx=3)
        self.train_label = ttk.Label(train_frame, text="80%", width=4)
        self.train_label.pack(side='right')
        
        # Val split
        val_frame = ttk.Frame(split_frame)
        val_frame.pack(fill='x', pady=1)
        ttk.Label(val_frame, text="Val:").pack(side='left')
        self.val_label = ttk.Label(val_frame, text="20%", width=4)
        self.val_label.pack(side='right')
        
        # Export options
        options_frame = ttk.Frame(export_frame)
        options_frame.pack(fill='x', padx=3, pady=2)
        
        self.include_confidence_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Include Confidence", 
                    variable=self.include_confidence_var).pack(anchor='w')
        
        self.create_yaml_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Create data.yaml", 
                    variable=self.create_yaml_var).pack(anchor='w')
        
        # Export buttons
        export_btn_frame = ttk.Frame(export_frame)
        export_btn_frame.pack(fill='x', padx=3, pady=3)
        
        ttk.Button(export_btn_frame, text="📤 Export Dataset", 
                command=self.export_dataset, width=button_width).pack(fill='x', pady=1)
        ttk.Button(export_btn_frame, text="💾 Save All Annotations", 
                command=self.save_all_annotations, width=button_width).pack(fill='x', pady=1)
        
    def create_bottom_panel(self):
        """Create console and status panel"""
        # Console
        console_frame = ttk.Frame(self.bottom_frame)
        console_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.console_text = scrolledtext.ScrolledText(console_frame, height=5, 
                                                     bg='#1e1e1e', fg='#00ff00',
                                                     font=('Consolas', 9))
        self.console_text.pack(fill='both', expand=True)
        
    def create_status_bar(self):
        """Create status bar"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill='x', side='bottom', padx=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var, 
                                     relief='sunken', anchor='w')
        self.status_label.pack(side='left', fill='x', expand=True, padx=(0,5))
        
        # Coordinates label
        self.coords_var = tk.StringVar(value="(0, 0)")
        self.coords_label = ttk.Label(self.status_frame, textvariable=self.coords_var,
                                     relief='sunken', width=12)
        self.coords_label.pack(side='right')
        
        # Annotation count label
        self.ann_count_var = tk.StringVar(value="Annotations: 0")
        self.ann_count_label = ttk.Label(self.status_frame, textvariable=self.ann_count_var,
                                        relief='sunken', width=15)
        self.ann_count_label.pack(side='right', padx=(0,5))
        
    def create_menus(self):
        """Create menu bar with Help menu"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # File menu 
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        
        # Project section
        file_menu.add_command(label="New Project", command=self.new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="Save Project...", command=self.save_project, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="Load Project...", command=self.load_project, accelerator="Ctrl+O")
        file_menu.add_separator()
        
        # Images section
        file_menu.add_command(label="Load Images...", command=self.load_images, accelerator="Ctrl+I")
        file_menu.add_command(label="Save Current", command=self.save_current, accelerator="Ctrl+S")
        file_menu.add_command(label="Save All Annotations", command=self.save_all_annotations)
        file_menu.add_separator()
        
        # Export section
        file_menu.add_command(label="Export Dataset...", command=self.export_dataset, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu 
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo_action, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Delete Selected", command=self.delete_selected, accelerator="Delete")
        edit_menu.add_command(label="Clear All", command=self.clear_all_annotations, accelerator="Ctrl+Shift+C")
        edit_menu.add_separator()
        edit_menu.add_command(label="Copy", command=self.copy_selected, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_annotation, accelerator="Ctrl+V")
        
        # View menu 
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Zoom Fit", command=self.zoom_fit, accelerator="Ctrl+0")
        view_menu.add_command(label="Reset View", command=self.reset_view, accelerator="Ctrl+R")
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Show Labels", variable=self.show_labels_var, command=self.toggle_labels)
        view_menu.add_checkbutton(label="Show Confidence", variable=self.show_conf_var, command=self.display_image)
        
        # Tools menu 
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Rectangle Tool", command=lambda: self.set_annotation_mode('rectangle'), accelerator="R")
        tools_menu.add_separator()
        tools_menu.add_command(label="Polygon Tool", command=lambda: self.show_coming_soon('polygon'), state='disabled')
        tools_menu.add_command(label="Point Tool", command=lambda: self.show_coming_soon('point'), state='disabled')
        tools_menu.add_command(label="Brush Tool", command=lambda: self.show_coming_soon('brush'), state='disabled')
        
        # NEW: Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        
        help_menu.add_command(label="Quick Start Guide", command=self.show_quick_start)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts, accelerator="F1")
        help_menu.add_separator()
        help_menu.add_command(label="Documentation", command=self.open_documentation)
        help_menu.add_command(label="GitHub Repository", command=self.open_github)
        help_menu.add_command(label="Report Bug", command=self.open_bug_report)
        help_menu.add_separator()
        help_menu.add_command(label="Check for Updates", command=self.check_for_updates)
        help_menu.add_separator()
        help_menu.add_command(label="About Annotex", command=self.show_about)

    def show_about(self):
        """Show About dialog with version info"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About Annotex")
        about_window.geometry("450x500")
        about_window.transient(self.root)
        about_window.grab_set()
        about_window.resizable(False, False)
        
        # Center the dialog
        about_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 50))
        
        # Main frame with padding
        main_frame = ttk.Frame(about_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # App icon/logo area
        icon_frame = ttk.Frame(main_frame)
        icon_frame.pack(pady=(0,20))
        
        app_icon = tk.Label(icon_frame, text="📋", font=("Arial", 48))
        app_icon.pack()
        
        # App info
        ttk.Label(main_frame, text="Annotex", font=("Arial", 20, "bold")).pack()
        ttk.Label(main_frame, text="Professional Image Annotation Tool", 
                font=("Arial", 11)).pack(pady=(0,10))
        
        # Version info
        version_frame = ttk.LabelFrame(main_frame, text="Version Information", padding="10")
        version_frame.pack(fill='x', pady=(10,0))
        
        info_text = [
            ("Version:", "2.1.0"),
            ("Release:", "August 2025"),
            ("Python:", f"{sys.version.split()[0]}"),
            ("Tkinter:", f"{tk.TkVersion}"),
            # ("PIL Available:", "Yes" if PIL_AVAILABLE else "No"),
            # ("YOLO Available:", "Yes" if hasattr(self, 'yolo_available') and self.yolo_available else "No")
        ]
        
        for label, value in info_text:
            row = ttk.Frame(version_frame)
            row.pack(fill='x', pady=1)
            ttk.Label(row, text=label, width=12, anchor='w').pack(side='left')
            ttk.Label(row, text=value, anchor='w').pack(side='left')
        
        # Features
        features_frame = ttk.LabelFrame(main_frame, text="Key Features", padding="10")
        features_frame.pack(fill='x', pady=(10,0))
        
        features = [
            "• Manual rectangle annotation tool",
            "• AI-powered auto-annotation",
            "• Dynamic class management",
            "• YOLO format export",
            # "• Project save/load functionality",
            "• Batch processing capabilities"
        ]
        
        for feature in features:
            ttk.Label(features_frame, text=feature, anchor='w').pack(anchor='w', pady=1)
        
        # Credits
        credits_frame = ttk.LabelFrame(main_frame, text="Credits", padding="10")
        credits_frame.pack(fill='x', pady=(10,0))
        
        credits_text = tk.Text(credits_frame, height=3, width=40, wrap=tk.WORD, 
                            font=("Arial", 9), bg=about_window.cget('bg'), relief='flat')
        credits_text.pack(fill='x')
        credits_text.insert('1.0', "Built with Python, Tkinter, PIL, OpenCV, and Ultralytics YOLO.\n"
                                "Designed for computer vision researchers and data scientists.")
        credits_text.config(state='disabled')
        
        # Close button
        ttk.Button(main_frame, text="Close", command=about_window.destroy, width=15).pack(pady=(15,0))

    def show_quick_start(self):
        """Show Quick Start Guide"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("Quick Start Guide")
        guide_window.geometry("600x500")
        guide_window.transient(self.root)
        guide_window.grab_set()
        
        # Center the dialog
        guide_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 30))
        
        # Create scrollable text widget
        main_frame = ttk.Frame(guide_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=70, height=25,
                                            font=("Arial", 10))
        text_widget.pack(fill='both', expand=True)
        
        guide_text = """ANNOTEX QUICK START GUIDE

    🚀 Getting Started:
    1. Click 'Load Images Folder' to select your image directory
    2. Add classes using the '+' button in Class Management
    3. Select a class and start annotating with the Rectangle tool
    4. Use arrow keys to navigate between images
    5. Export your dataset when ready

    📋 Basic Annotation Workflow:
    • Load images → Add classes → Annotate → Export
    • Rectangle tool: Click and drag to create bounding boxes
    • Each annotation is automatically assigned to the selected class
    • Auto-save keeps your work safe

    🎯 AI-Powered Features:
    • Load a YOLO model (.pt file) for auto-annotation
    • Adjust confidence threshold (0.1-1.0)
    • Use 'Auto Current' for single images
    • Use 'Auto All' for batch processing

    ⌨️ Essential Shortcuts:
    • Arrow Keys: Navigate images
    • Ctrl+S: Save current annotations
    • Ctrl+E: Export dataset
    • Delete: Remove selected annotation
    • Ctrl+Z: Undo last action

    💡 Pro Tips:
    • Start with a few images to test your workflow
    • Use consistent class names across projects
    • Save projects (.anno files) for easy resumption
    • Check annotation files in the 'annotations' folder

    📤 Export Options:
    • YOLO11/YOLOv8 formats supported
    • Customizable train/validation splits
    • Includes data.yaml for training
    • Maintains annotation confidence scores

    For detailed documentation, visit the GitHub repository or use Help → Documentation."""
        
        text_widget.insert('1.0', guide_text)
        text_widget.config(state='disabled')
        
        # Close button
        ttk.Button(guide_window, text="Close", command=guide_window.destroy).pack(pady=5)

    def show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        shortcuts_window = tk.Toplevel(self.root)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("400x300")
        shortcuts_window.transient(self.root)
        shortcuts_window.grab_set()
        
        # Center the dialog
        shortcuts_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 50))
        
        # Create main frame
        main_frame = ttk.Frame(shortcuts_window, padding="15")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        ttk.Label(main_frame, text="Keyboard Shortcuts", font=("Arial", 16, "bold")).pack(pady=(0,15))
        
        # Create notebook for categories
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Navigation shortcuts
        nav_frame = ttk.Frame(notebook, padding="10")
        notebook.add(nav_frame, text="Navigation")
        
        nav_shortcuts = [
            ("Left Arrow", "Previous image"),
            ("Right Arrow", "Next image"),
            ("Home", "First image"),
            ("End", "Last image"),
            ("Ctrl + +", "Zoom in"),
            ("Ctrl + -", "Zoom out"),
            ("Ctrl + 0", "Zoom fit"),
            ("Ctrl + R", "Reset view"),
        ]
        
        self.create_shortcut_list(nav_frame, nav_shortcuts)
        
        # File shortcuts
        file_frame = ttk.Frame(notebook, padding="10")
        notebook.add(file_frame, text="File Operations")
        
        file_shortcuts = [
            ("Ctrl + N", "New project"),
            ("Ctrl + O", "Open project"),
            ("Ctrl + S", "Save current"),
            ("Ctrl + Shift + S", "Save project"),
            ("Ctrl + I", "Load images"),
            ("Ctrl + E", "Export dataset"),
        ]
        
        self.create_shortcut_list(file_frame, file_shortcuts)
        
        # Edit shortcuts
        edit_frame = ttk.Frame(notebook, padding="10")
        notebook.add(edit_frame, text="Editing")
        
        edit_shortcuts = [
            ("Ctrl + Z", "Undo"),
            ("Ctrl + C", "Copy annotation"),
            ("Ctrl + V", "Paste annotation"),
            ("Delete", "Delete selected"),
            ("Ctrl + Shift + C", "Clear all"),
            ("R", "Rectangle tool"),
        ]
        
        self.create_shortcut_list(edit_frame, edit_shortcuts)
        
        # Tool shortcuts
        tool_frame = ttk.Frame(notebook, padding="10")
        notebook.add(tool_frame, text="Tools & Classes")
        
        tool_shortcuts = [
            ("1-9", "Select class by number"),
            ("F1", "Show shortcuts"),
            ("Middle Click + Drag", "Pan image"),
            ("Mouse Wheel", "Zoom in/out"),
            ("Right Click", "Context menu"),
        ]
        
        self.create_shortcut_list(tool_frame, tool_shortcuts)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=shortcuts_window.destroy, width=15).pack(pady=(10,0))

    def create_shortcut_list(self, parent, shortcuts):
        """Create a formatted list of shortcuts"""
        for key, description in shortcuts:
            row = ttk.Frame(parent)
            row.pack(fill='x', pady=2)
            
            key_label = ttk.Label(row, text=key, width=15, anchor='w', 
                                font=("Consolas", 9, "bold"))
            key_label.pack(side='left')
            
            desc_label = ttk.Label(row, text=description, anchor='w')
            desc_label.pack(side='left', padx=(10,0))

    def open_documentation(self):
        """Open documentation in browser"""
        import webbrowser
        webbrowser.open("https://github.com/RandikaKM/annotex/wiki")
        self.log_message("Opened documentation in browser")

    def open_github(self):
        """Open GitHub repository in browser"""
        import webbrowser
        webbrowser.open("https://github.com/RandikaKM/annotex")
        self.log_message("Opened GitHub repository in browser")

    def open_bug_report(self):
        """Open bug report page in browser"""
        import webbrowser
        webbrowser.open("https://github.com/RandikaKM/annotex/issues/new")
        self.log_message("Opened bug report page in browser")

    def check_for_updates(self):
        """Check for application updates"""
        # In a real application, you'd check against GitHub releases API
        messagebox.showinfo("Check for Updates", 
                        "You are running Annotex v2.1.0\n\n"
                        "To check for updates, visit:\n"
                        "https://github.com/RandikaKM/annotex/releases")
        
        self.log_message("Checked for updates")
            
    def setup_bindings(self):
        """Setup keyboard and mouse bindings - only rectangle tool active"""
        # Project shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_project())
        self.root.bind('<Control-Shift-S>', lambda e: self.save_project())
        self.root.bind('<Control-o>', lambda e: self.load_project())
        self.root.bind('<F1>', lambda e: self.show_shortcuts())
        
        # File shortcuts
        self.root.bind('<Control-i>', lambda e: self.load_images())
        self.root.bind('<Control-s>', lambda e: self.save_current())
        self.root.bind('<Control-e>', lambda e: self.export_dataset())
        
        # Edit shortcuts
        self.root.bind('<Control-z>', lambda e: self.undo_action())
        self.root.bind('<Control-c>', lambda e: self.copy_selected())
        self.root.bind('<Control-v>', lambda e: self.paste_annotation())
        self.root.bind('<Delete>', lambda e: self.delete_selected())
        self.root.bind('<Control-Shift-C>', lambda e: self.clear_all_annotations())
        
        # Navigation
        self.root.bind('<Left>', lambda e: self.prev_image())
        self.root.bind('<Right>', lambda e: self.next_image())
        self.root.bind('<Home>', lambda e: self.first_image())
        self.root.bind('<End>', lambda e: self.last_image())
        
        # View controls
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.zoom_fit())
        self.root.bind('<Control-r>', lambda e: self.reset_view())
        
        # Canvas mouse events
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        self.canvas.bind('<Button-3>', self.on_canvas_right_click)
        self.canvas.bind('<Motion>', self.on_canvas_motion)
        self.canvas.bind('<MouseWheel>', self.on_mouse_wheel)
        
        # Middle mouse button for panning
        self.canvas.bind('<Button-2>', self.start_pan)
        self.canvas.bind('<B2-Motion>', self.do_pan)
        self.canvas.bind('<ButtonRelease-2>', self.end_pan)
        
        # Tool shortcuts - only rectangle works
        self.root.bind('r', lambda e: self.set_annotation_mode('rectangle'))
        self.root.bind('p', lambda e: self.show_coming_soon('polygon'))
        self.root.bind('o', lambda e: self.show_coming_soon('point'))
        self.root.bind('b', lambda e: self.show_coming_soon('brush'))
        
        # Number keys for class selection
        for i in range(min(10, len(self.classes))):
            self.root.bind(str(i), lambda e, idx=i: self.select_class(idx))
            
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        self.canvas_width = event.width
        self.canvas_height = event.height
    
    # ==================== Core Methods ====================
    
    def log_message(self, message):
        """Add message to console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_status(self, message):
        """Update status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def update_annotation_count(self):
        """Update annotation count display"""
        count = len(self.current_annotations)
        self.ann_count_var.set(f"Annotations: {count}")
        
    # ==================== Class Management ====================
    
    def add_class(self, name=None, color=None):
        """Add a new class"""
        if name is None:
            return
            
        class_info = {
            'id': self.next_class_id,
            'name': name,
            'color': color or f"#{self.next_class_id*50 % 200 + 55:02x}{self.next_class_id*80 % 200 + 55:02x}{self.next_class_id*120 % 200 + 55:02x}"
        }
        
        self.classes.append(class_info)
        self.next_class_id += 1
        self.update_class_list()
        self.log_message(f"Added class: {name}")
        
    def add_class_dialog(self):
        """Show dialog to add new class"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Class")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Class name
        ttk.Label(dialog, text="Class Name:").pack(pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        # Color selection
        color_frame = ttk.Frame(dialog)
        color_frame.pack(pady=5)
        
        ttk.Label(color_frame, text="Color:").pack(side='left')
        color_var = tk.StringVar(value="#00FF00")
        color_display = tk.Label(color_frame, text="     ", bg=color_var.get(), width=5)
        color_display.pack(side='left', padx=5)
        
        def choose_color():
            color = colorchooser.askcolor(title="Choose Class Color")[1]
            if color:
                color_var.set(color)
                color_display.config(bg=color)
                
        ttk.Button(color_frame, text="Choose Color", command=choose_color).pack(side='left')
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        def add_class_action():
            name = name_var.get().strip()
            if name:
                # Check if class name already exists
                existing_names = [cls['name'] for cls in self.classes]
                if name in existing_names:
                    messagebox.showerror("Error", "Class name already exists!")
                    return
                    
                self.add_class(name, color_var.get())
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Please enter a class name!")
                
        ttk.Button(btn_frame, text="Add", command=add_class_action).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)
        
        # Enter key to add
        name_entry.bind('<Return>', lambda e: add_class_action())
        
    def edit_class(self):
        """Edit selected class"""
        selection = self.class_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a class to edit")
            return
            
        class_idx = selection[0]
        if class_idx >= len(self.classes):
            return
            
        class_info = self.classes[class_idx]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Class")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Class name
        ttk.Label(dialog, text="Class Name:").pack(pady=5)
        name_var = tk.StringVar(value=class_info['name'])
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        # Color selection
        color_frame = ttk.Frame(dialog)
        color_frame.pack(pady=5)
        
        ttk.Label(color_frame, text="Color:").pack(side='left')
        color_var = tk.StringVar(value=class_info['color'])
        color_display = tk.Label(color_frame, text="     ", bg=color_var.get(), width=5)
        color_display.pack(side='left', padx=5)
        
        def choose_color():
            color = colorchooser.askcolor(title="Choose Class Color")[1]
            if color:
                color_var.set(color)
                color_display.config(bg=color)
                
        ttk.Button(color_frame, text="Choose Color", command=choose_color).pack(side='left')
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        def save_changes():
            new_name = name_var.get().strip()
            if new_name:
                # Check if new name conflicts with other classes
                existing_names = [cls['name'] for i, cls in enumerate(self.classes) if i != class_idx]
                if new_name in existing_names:
                    messagebox.showerror("Error", "Class name already exists!")
                    return
                    
                self.classes[class_idx]['name'] = new_name
                self.classes[class_idx]['color'] = color_var.get()
                self.update_class_list()
                self.display_image()  # Refresh display with new colors
                self.log_message(f"Updated class: {new_name}")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Please enter a class name!")
                
        ttk.Button(btn_frame, text="Save", command=save_changes).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)
        
    def delete_class(self):
        """Delete selected class"""
        selection = self.class_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a class to delete")
            return
            
        class_idx = selection[0]
        if class_idx >= len(self.classes):
            return
            
        class_info = self.classes[class_idx]
        
        # Check if class is used in current annotations
        used_in_annotations = any(ann['class_id'] == class_info['id'] for ann in self.current_annotations)
        
        if used_in_annotations:
            if not messagebox.askyesno("Class In Use", 
                                     f"Class '{class_info['name']}' is used in current annotations.\n"
                                     f"Delete anyway? This will remove those annotations."):
                return
                
        if messagebox.askyesno("Confirm Delete", f"Delete class '{class_info['name']}'?"):
            # Remove annotations with this class
            self.current_annotations = [ann for ann in self.current_annotations 
                                      if ann['class_id'] != class_info['id']]
            
            # Remove class
            del self.classes[class_idx]
            
            # Update selected class if necessary
            if self.selected_class_id == class_info['id']:
                self.selected_class_id = self.classes[0]['id'] if self.classes else 0
                
            self.update_class_list()
            self.display_image()
            self.update_annotation_count()
            self.log_message(f"Deleted class: {class_info['name']}")
            
    def update_class_list(self):
        """Update class list display"""
        self.class_listbox.delete(0, tk.END)
        
        for i, class_info in enumerate(self.classes):
            display_text = f"● {class_info['name']}"
            self.class_listbox.insert(tk.END, display_text)
            
            # Set background color
            try:
                self.class_listbox.itemconfig(i, {'bg': class_info['color'], 'fg': 'white'})
            except tk.TclError:
                pass  # Ignore color errors
                
        # Update current selected class display
        if self.classes:
            selected_class = self.get_class_by_id(self.selected_class_id)
            if selected_class:
                self.current_class_label.config(text=selected_class['name'], 
                                              background=selected_class['color'])
            else:
                # Select first class if current selection is invalid
                self.selected_class_id = self.classes[0]['id']
                self.current_class_label.config(text=self.classes[0]['name'], 
                                              background=self.classes[0]['color'])
        else:
            self.current_class_label.config(text="No class", background='lightgray')
            
    def on_class_select(self, event):
        """Handle class selection"""
        selection = self.class_listbox.curselection()
        if selection and selection[0] < len(self.classes):
            class_info = self.classes[selection[0]]
            self.selected_class_id = class_info['id']
            self.current_class_label.config(text=class_info['name'], 
                                          background=class_info['color'])
            self.update_status(f"Selected class: {class_info['name']}")
            
    def select_class(self, index):
        """Select class by index"""
        if 0 <= index < len(self.classes):
            self.selected_class_id = self.classes[index]['id']
            self.class_listbox.selection_clear(0, tk.END)
            self.class_listbox.selection_set(index)
            self.update_class_list()
            
    def get_class_by_id(self, class_id):
        """Get class info by ID with validation"""
        for class_info in self.classes:
            if class_info['id'] == class_id:
                return class_info
        
        # Return default if not found and we have classes
        if self.classes:
            self.log_message(f"⚠️ Class ID {class_id} not found, using first class")
            return self.classes[0]
        
        # Return None if no classes exist
        return None

    def create_tooltip(self, widget, text):
        """Create tooltip for widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="white", font=("Arial", 9))
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
    # ==================== Image Management ====================
    
    def load_images(self):
        """Load images from directory"""
        directory = filedialog.askdirectory(title="Select Images Directory")
        if not directory:
            return
            
        self.log_message(f"Loading images from: {directory}")
        
        # Get image files
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp')
        self.image_list = []
        
        for ext in image_extensions:
            self.image_list.extend(Path(directory).glob(f"*{ext}"))
            self.image_list.extend(Path(directory).glob(f"*{ext.upper()}"))
        
        self.image_list = sorted(list(set(self.image_list)))
        
        if not self.image_list:
            messagebox.showwarning("No Images", "No image files found in the selected directory")
            return
            
        # Update image listbox
        self.update_image_listbox()
            
        self.current_image_index = 0
        self.load_current_image()
        self.update_image_counter()
        
        self.log_message(f"Loaded {len(self.image_list)} images")
        
    def load_current_image(self):
        """Load and display current image"""
        if not self.image_list:
            return
            
        self.current_image_path = self.image_list[self.current_image_index]
        
        try:
            # Validate file exists and is readable
            if not self.current_image_path.exists():
                raise FileNotFoundError(f"Image file not found: {self.current_image_path}")
                
            # Check file size
            if self.current_image_path.stat().st_size == 0:
                raise ValueError("Image file is empty")
            
            # Load image with PIL
            if PIL_AVAILABLE:
                self.original_image = Image.open(self.current_image_path)
                if self.original_image.mode != 'RGB':
                    self.original_image = self.original_image.convert('RGB')
                self.current_image = self.original_image.copy()
            else:
                # Fallback to OpenCV
                img = cv2.imread(str(self.current_image_path))
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                self.original_image = Image.fromarray(img)
                self.current_image = self.original_image.copy()
            
            # Load annotations
            self.load_annotations()
            
            # Reset view
            self.zoom_factor = 1.0
            self.pan_x = 0
            self.pan_y = 0
            
            # Display image
            self.display_image()
            
            # Update UI
            self.update_image_list_selection()
            self.update_image_info()
            self.update_annotation_count()
            
            self.update_status(f"Loaded: {self.current_image_path.name}")
            
        except Exception as e:
            self.log_message(f"Error loading image: {e}")
            messagebox.showerror("Error", f"Could not load image: {e}")
            
    def display_image(self):
        """Display current image with annotations on canvas"""
        if not self.current_image:
            return
            
        # Clean up previous image to free memory
        if hasattr(self, 'photo_image'):
            del self.photo_image
            
        # Calculate display size
        img_width, img_height = self.current_image.size
        display_width = int(img_width * self.zoom_factor)
        display_height = int(img_height * self.zoom_factor)
        
        # Create display image
        if self.zoom_factor != 1.0:
            display_image = self.current_image.resize((display_width, display_height), Image.LANCZOS)
        else:
            display_image = self.current_image.copy()
            
        # Draw annotations
        if self.current_annotations:
            display_image = self.draw_annotations_on_image(display_image)
            
        # Convert to PhotoImage
        self.photo_image = ImageTk.PhotoImage(display_image)
        
        # Clear canvas and add image
        self.canvas.delete("all")
        image_id = self.canvas.create_image(self.pan_x, self.pan_y, anchor='nw', image=self.photo_image)
        
        # Update scroll region
        bbox = self.canvas.bbox(image_id)
        if bbox:
            self.canvas.configure(scrollregion=bbox)
            
        # Update zoom label
        self.zoom_label.config(text=f"{int(self.zoom_factor * 100)}%")

        
    def draw_annotations_on_image(self, image):
        """Draw annotations on PIL image"""
        if not self.current_annotations:
            return image
            
        draw = ImageDraw.Draw(image)
        
        # Try to load a font
        try:
            font = ImageFont.truetype("arial.ttf", int(14 * self.zoom_factor))
        except:
            font = ImageFont.load_default()
            
        for i, ann in enumerate(self.current_annotations):
            class_info = self.get_class_by_id(ann['class_id'])
            if not class_info:
                continue
                
            color = class_info['color']
            
            # Scale coordinates
            if ann['type'] == 'rectangle':
                x = int(ann['x'] * self.zoom_factor)
                y = int(ann['y'] * self.zoom_factor)
                w = int(ann['w'] * self.zoom_factor)
                h = int(ann['h'] * self.zoom_factor)
                
                # Draw rectangle
                outline_width = 3 if i == self.selected_annotation else 2
                draw.rectangle([x, y, x + w, y + h], outline=color, width=outline_width)
                
                # Highlight selected annotation
                if i == self.selected_annotation:
                    draw.rectangle([x-2, y-2, x + w + 2, y + h + 2], outline='yellow', width=1)
                    
                    # Draw resize handles
                    handle_size = 6
                    handles = [
                        (x, y), (x + w//2, y), (x + w, y),
                        (x, y + h//2), (x + w, y + h//2),
                        (x, y + h), (x + w//2, y + h), (x + w, y + h)
                    ]
                    
                    for hx, hy in handles:
                        draw.rectangle([hx-handle_size//2, hy-handle_size//2, 
                                      hx+handle_size//2, hy+handle_size//2], 
                                     fill='yellow', outline='black')
                
                # Draw label
                if self.show_labels_var.get():
                    label_text = class_info['name']
                    if self.show_conf_var.get() and 'confidence' in ann:
                        label_text += f" ({ann['confidence']:.2f})"
                        
                    # Get text dimensions
                    text_bbox = draw.textbbox((0, 0), label_text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    
                    # Position label above box
                    label_y = max(0, y - text_height - 4)
                    
                    # Simple background rectangle
                    draw.rectangle([x, label_y, x + text_width + 8, label_y + text_height + 4], 
                                fill=color)
                    
                    # Simple white text
                    draw.text((x + 4, label_y + 2), label_text, fill='white', font=font)
                    
            elif ann['type'] == 'polygon':
                # Scale polygon points
                scaled_points = []
                for px, py in ann['points']:
                    scaled_points.extend([int(px * self.zoom_factor), int(py * self.zoom_factor)])
                    
                if len(scaled_points) >= 6:  # At least 3 points
                    outline_width = 3 if i == self.selected_annotation else 2
                    draw.polygon(scaled_points, outline=color, width=outline_width)
                    
                    if i == self.selected_annotation:
                        # Draw polygon points
                        for j in range(0, len(scaled_points), 2):
                            px, py = scaled_points[j], scaled_points[j+1]
                            draw.ellipse([px-4, py-4, px+4, py+4], fill='yellow', outline='black')
                            
            elif ann['type'] == 'point':
                px = int(ann['x'] * self.zoom_factor)
                py = int(ann['y'] * self.zoom_factor)
                
                size = 8 if i == self.selected_annotation else 6
                draw.ellipse([px-size, py-size, px+size, py+size], 
                           fill=color, outline='white', width=2)
                           
                if self.show_labels_var.get():
                    draw.text((px + 10, py - 10), class_info['name'], fill=color, font=font)
                    
        return image
        
    def load_annotations(self):
        """Load annotations for current image from separate folder"""
        if not self.current_image_path:
            return
            
        # Look for annotations in separate folder
        image_folder = self.current_image_path.parent
        annotations_folder = image_folder / "annotations"
        annotation_filename = self.current_image_path.stem + '.txt'
        annotation_path = annotations_folder / annotation_filename
        
        self.current_annotations = []
        
        if annotation_path.exists():
            try:
                with open(annotation_path, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            class_id = int(parts[0])
                            x_center = float(parts[1])
                            y_center = float(parts[2])
                            width = float(parts[3])
                            height = float(parts[4])
                            
                            # Convert from YOLO format to pixel coordinates
                            img_width, img_height = self.current_image.size
                            x = int((x_center - width/2) * img_width)
                            y = int((y_center - height/2) * img_height)
                            w = int(width * img_width)
                            h = int(height * img_height)
                            
                            annotation = {
                                'type': 'rectangle',
                                'class_id': class_id,
                                'x': x,
                                'y': y,
                                'w': w,
                                'h': h
                            }
                            
                            if len(parts) > 5:
                                annotation['confidence'] = float(parts[5])
                                
                            self.current_annotations.append(annotation)
                            
                self.log_message(f"Loaded {len(self.current_annotations)} annotations")
                
            except Exception as e:
                self.log_message(f"Error loading annotations: {e}")
                
    def save_current(self):
        """Save annotations for current image"""
        if not self.current_image_path or not self.current_image:
            return
            
        self.save_annotations()
        
    def save_annotations(self):
        """Save annotations for current image to separate folder"""
        if not self.current_image_path or not self.current_image:
            return
            
        # Create annotations folder next to image folder
        image_folder = self.current_image_path.parent
        annotations_folder = image_folder / "annotations"
        annotations_folder.mkdir(exist_ok=True)
        
        # Save annotation file in separate folder
        annotation_filename = self.current_image_path.stem + '.txt'
        annotation_path = annotations_folder / annotation_filename
        
        try:
            with open(annotation_path, 'w') as f:
                img_width, img_height = self.current_image.size
                
                for ann in self.current_annotations:
                    if ann['type'] == 'rectangle':
                        # Convert to YOLO format
                        x_center = (ann['x'] + ann['w']/2) / img_width
                        y_center = (ann['y'] + ann['h']/2) / img_height
                        width = ann['w'] / img_width
                        height = ann['h'] / img_height
                        
                        line = f"{ann['class_id']} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
                        
                        # FIXED: Check the checkbox before including confidence
                        if 'confidence' in ann and self.include_confidence_var.get():
                            line += f" {ann['confidence']:.6f}"
                            
                        f.write(line + '\n')
                        
            self.log_message(f"Saved annotations to: {annotation_path}")
            
        except Exception as e:
            self.log_message(f"Error saving annotations: {e}")
            
    def update_image_list_annotation_status(self):
        """Update annotation status markers in image list"""
        if not self.image_list:
            return
            
        # Check annotations folder instead of same folder
        image_folder = self.current_image_path.parent
        annotations_folder = image_folder / "annotations"
        annotation_filename = self.current_image_path.stem + '.txt'
        annotation_path = annotations_folder / annotation_filename
        
        status = "✓" if annotation_path.exists() else "○"
        
        # Update listbox item
        current_name = self.current_image_path.name
        new_text = f"{status} {current_name}"
        
        try:
            self.image_listbox.delete(self.current_image_index)
            self.image_listbox.insert(self.current_image_index, new_text)
            self.image_listbox.selection_set(self.current_image_index)
        except:
            pass
            
    # ==================== Navigation Methods ====================
    
    def next_image(self):
        """Navigate to next image"""
        if not self.image_list:
            return
            
        if self.auto_save and self.current_annotations:
            self.save_annotations()
            
        self.current_image_index = (self.current_image_index + 1) % len(self.image_list)
        self.load_current_image()
        self.update_image_counter()
        
    def prev_image(self):
        """Navigate to previous image"""
        if not self.image_list:
            return
            
        if self.auto_save and self.current_annotations:
            self.save_annotations()
            
        self.current_image_index = (self.current_image_index - 1) % len(self.image_list)
        self.load_current_image()
        self.update_image_counter()
        
    def first_image(self):
        """Navigate to first image"""
        if not self.image_list:
            return
            
        if self.auto_save and self.current_annotations:
            self.save_annotations()
            
        self.current_image_index = 0
        self.load_current_image()
        self.update_image_counter()
        
    def last_image(self):
        """Navigate to last image"""
        if not self.image_list:
            return
            
        if self.auto_save and self.current_annotations:
            self.save_annotations()
            
        self.current_image_index = len(self.image_list) - 1
        self.load_current_image()
        self.update_image_counter()
        
    def update_image_counter(self):
        """Update image counter display"""
        if self.image_list:
            self.image_counter.config(text=f"{self.current_image_index + 1}/{len(self.image_list)}")
        else:
            self.image_counter.config(text="0/0")
            
    def update_image_list_selection(self):
        """Update image listbox selection"""
        if self.image_list:
            self.image_listbox.selection_clear(0, tk.END)
            self.image_listbox.selection_set(self.current_image_index)
            self.image_listbox.see(self.current_image_index)
            
    def update_image_info(self):
        """Update image information display"""
        if self.current_image and self.current_image_path:
            width, height = self.current_image.size
            file_size = self.current_image_path.stat().st_size // 1024  # KB
            info_text = f"{width}x{height} • {file_size}KB"
            self.image_info_label.config(text=info_text)
        else:
            self.image_info_label.config(text="No image loaded")
            
    def on_image_select(self, event):
        """Handle image list selection"""
        selection = self.image_listbox.curselection()
        if selection and selection[0] != self.current_image_index:
            if self.auto_save and self.current_annotations:
                self.save_annotations()
                
            self.current_image_index = selection[0]
            self.load_current_image()
            self.update_image_counter()
            
    # ==================== View Control Methods ====================
    
    def zoom_in(self):
        """Zoom in on image"""
        if self.current_image:
            self.zoom_factor = min(self.zoom_factor * 1.25, 10.0)
            self.display_image()
            
    def zoom_out(self):
        """Zoom out on image"""
        if self.current_image:
            self.zoom_factor = max(self.zoom_factor / 1.25, 0.1)
            self.display_image()
            
    def zoom_fit(self):
        """Fit image to canvas"""
        if not self.current_image:
            return
            
        img_width, img_height = self.current_image.size
        
        # Get canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
            
        # Calculate zoom factor to fit image in canvas
        zoom_x = (canvas_width - 20) / img_width
        zoom_y = (canvas_height - 20) / img_height
        
        self.zoom_factor = min(zoom_x, zoom_y, 1.0) 
        self.pan_x = 0
        self.pan_y = 0
        
        self.display_image()
        
    def reset_view(self):
        """Reset view to original"""
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        if self.current_image:
            self.display_image()
            
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for zooming"""
        if self.current_image:
            if event.delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
                
    def start_pan(self, event):
        """Start panning"""
        self.is_panning = True
        self.last_x = event.x
        self.last_y = event.y
        self.cursor_label.config(text='✋')
        
    def do_pan(self, event):
        """Pan the image"""
        if self.is_panning:
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            
            self.pan_x += dx
            self.pan_y += dy
            
            self.last_x = event.x
            self.last_y = event.y
            
            self.display_image()
            
    def end_pan(self, event):
        """End panning"""
        self.update_cursor_indicator()
        self.is_panning = False
        
        
    # ==================== Annotation Tool Methods ====================
    
    def set_annotation_mode(self, mode):
        """Set annotation tool mode - only rectangle is functional"""
        # Only allow rectangle mode for now
        if mode != "rectangle":
            self.show_coming_soon(mode)
            return
            
        self.annotation_mode = mode
        
        # Update button states
        for tool_mode, button in self.tool_buttons.items():
            if tool_mode == mode:
                button.config(relief='sunken', bg='#4CAF50', fg='white')
            elif tool_mode == 'rectangle':
                button.config(relief='raised', bg='#4CAF50', fg='white')
            else:
                # Keep coming soon buttons grayed out
                button.config(relief='raised', bg='#E0E0E0', fg='#888888')
                
        # Reset drawing state
        self.is_drawing = False
        self.current_polygon_points = []
        self.selected_annotation = None
        
        # Update UI indicators
        if hasattr(self, 'mode_label') and self.mode_label:
            self.mode_label.config(text=f"Mode: {mode.title()}")

        self.update_cursor_indicator()
        
        if hasattr(self, 'status_var'):
            self.update_status(f"Mode: {mode.title()}")
        if hasattr(self, 'console_text'):
            self.log_message(f"Switched to {mode} tool")
    
    def update_cursor_indicator(self):
        """Update cursor indicator"""
        if hasattr(self, 'cursor_label') and self.cursor_label:
            cursors = {
                'rectangle': '🔲',
                'polygon': '🔷', 
                'point': '📍',
                'brush': '🖌️'
            }
            self.cursor_label.config(text=cursors.get(self.annotation_mode, '🖱️'))
        
    def update_brush_size(self, value=None):
        """Update brush size"""
        self.brush_size = int(float(self.brush_var.get()))
        
    def toggle_labels(self):
        """Toggle label display"""
        self.show_labels = self.show_labels_var.get()
        self.display_image()
        
    # ==================== Canvas Event Handlers ====================
    
    def on_canvas_click(self, event):
        """Handle canvas click events"""
        if not self.current_image:
            return
            
        # Convert canvas coordinates to image coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Adjust for pan
        img_x = int((canvas_x - self.pan_x) / self.zoom_factor)
        img_y = int((canvas_y - self.pan_y) / self.zoom_factor)
        
        # Check if clicking on existing annotation
        clicked_annotation = self.find_annotation_at_point(img_x, img_y)
        
        if clicked_annotation is not None:
            self.selected_annotation = clicked_annotation
            self.display_image()
            self.update_status(f"Selected annotation {clicked_annotation + 1}")
            return
            
        # Handle different annotation modes
        if self.annotation_mode == "rectangle":
            self.start_rectangle(img_x, img_y)
        elif self.annotation_mode == "polygon":
            self.add_polygon_point(img_x, img_y)
        elif self.annotation_mode == "point":
            self.add_point_annotation(img_x, img_y)
        elif self.annotation_mode == "brush":
            self.start_brush_stroke(img_x, img_y)
            
    def on_canvas_drag(self, event):
        """Handle canvas drag events"""
        if not self.current_image:
            return
            
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        img_x = int((canvas_x - self.pan_x) / self.zoom_factor)
        img_y = int((canvas_y - self.pan_y) / self.zoom_factor)
        
        if self.annotation_mode == "rectangle" and self.is_drawing:
            self.update_rectangle(img_x, img_y)
        elif self.annotation_mode == "brush" and self.is_drawing:
            self.continue_brush_stroke(img_x, img_y)
            
    def on_canvas_release(self, event):
        """Handle canvas mouse release events"""
        if not self.current_image:
            return
            
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        img_x = int((canvas_x - self.pan_x) / self.zoom_factor)
        img_y = int((canvas_y - self.pan_y) / self.zoom_factor)
        
        if self.annotation_mode == "rectangle" and self.is_drawing:
            self.finish_rectangle(img_x, img_y)
        elif self.annotation_mode == "brush" and self.is_drawing:
            self.finish_brush_stroke()
            
    def on_canvas_right_click(self, event):
        """Handle right-click context menu"""
        if self.annotation_mode == "polygon" and self.current_polygon_points:
            # Finish polygon on right-click
            self.finish_polygon()
        else:
            # Show context menu
            self.show_context_menu(event)
            
    def on_canvas_motion(self, event):
        """Handle canvas mouse motion"""
        if not self.current_image:
            return
            
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        img_x = int((canvas_x - self.pan_x) / self.zoom_factor)
        img_y = int((canvas_y - self.pan_y) / self.zoom_factor)
        
        # Update coordinates display
        self.coords_var.set(f"({img_x}, {img_y})")

        
    # ==================== Rectangle Annotation ====================
    
    def start_rectangle(self, x, y):
        """Start drawing rectangle"""
        self.is_drawing = True
        self.start_x = x
        self.start_y = y
        self.selected_annotation = None
        
    def update_rectangle(self, x, y):
        """Update rectangle while dragging"""
        if not self.is_drawing:
            return
            
        # Calculate current rectangle
        min_x = min(self.start_x, x)
        min_y = min(self.start_y, y)
        width = abs(x - self.start_x)
        height = abs(y - self.start_y)
        
        self.current_bbox = (min_x, min_y, width, height)
        self.display_image_with_temp_annotation()
        
    def finish_rectangle(self, x, y):
        """Finish drawing rectangle"""
        if not self.is_drawing:
            return
            
        self.is_drawing = False
        
        # Calculate final rectangle
        min_x = min(self.start_x, x)
        min_y = min(self.start_y, y)
        width = abs(x - self.start_x)
        height = abs(y - self.start_y)
        
        # Only add if rectangle is large enough
        if width > 5 and height > 5:
            self.add_rectangle_annotation(min_x, min_y, width, height)
            
        self.current_bbox = None
        self.display_image()
        
    def add_rectangle_annotation(self, x, y, w, h):
        """Add rectangle annotation"""
        if not self.classes:
            messagebox.showwarning("No Classes", "Please add at least one class before annotating")
            return
            
        annotation = {
            'type': 'rectangle',
            'class_id': self.selected_class_id,
            'x': max(0, x),
            'y': max(0, y),
            'w': max(1, w),
            'h': max(1, h)
        }
        
        self.current_annotations.append(annotation)
        self.update_annotation_count()
        
        if self.auto_save:
            self.save_annotations()
            
        class_info = self.get_class_by_id(self.selected_class_id)
        class_name = class_info['name'] if class_info else f"Class_{self.selected_class_id}"
        self.log_message(f"Added rectangle: {class_name}")
        
    # ==================== Polygon Annotation ====================
    
    def add_polygon_point(self, x, y):
        """Add point to current polygon"""
        self.current_polygon_points.append((x, y))
        
        if len(self.current_polygon_points) == 1:
            self.log_message("Started polygon. Right-click to finish.")
            
        self.display_image_with_temp_annotation()
        
    def finish_polygon(self):
        """Finish current polygon"""
        if len(self.current_polygon_points) < 3:
            messagebox.showwarning("Invalid Polygon", "Polygon must have at least 3 points")
            self.current_polygon_points = []
            self.display_image()
            return
            
        if not self.classes:
            messagebox.showwarning("No Classes", "Please add at least one class before annotating")
            self.current_polygon_points = []
            self.display_image()
            return
            
        annotation = {
            'type': 'polygon',
            'class_id': self.selected_class_id,
            'points': self.current_polygon_points.copy()
        }
        
        self.current_annotations.append(annotation)
        self.current_polygon_points = []
        self.update_annotation_count()
        
        if self.auto_save:
            self.save_annotations()
            
        class_info = self.get_class_by_id(self.selected_class_id)
        class_name = class_info['name'] if class_info else f"Class_{self.selected_class_id}"
        self.log_message(f"Added polygon: {class_name}")
        self.display_image()
        
    # ==================== Point Annotation ====================
    
    def add_point_annotation(self, x, y):
        """Add point annotation"""
        if not self.classes:
            messagebox.showwarning("No Classes", "Please add at least one class before annotating")
            return
            
        annotation = {
            'type': 'point',
            'class_id': self.selected_class_id,
            'x': x,
            'y': y
        }
        
        self.current_annotations.append(annotation)
        self.update_annotation_count()
        
        if self.auto_save:
            self.save_annotations()
            
        class_info = self.get_class_by_id(self.selected_class_id)
        class_name = class_info['name'] if class_info else f"Class_{self.selected_class_id}"
        self.log_message(f"Added point: {class_name}")
        self.display_image()
        
    # ==================== Brush Annotation ====================
    
    def start_brush_stroke(self, x, y):
        """Start brush stroke"""
        self.is_drawing = True
        # For simplicity, treat brush as small rectangles
        self.add_brush_point(x, y)
        
    def continue_brush_stroke(self, x, y):
        """Continue brush stroke"""
        if self.is_drawing:
            self.add_brush_point(x, y)
            
    def finish_brush_stroke(self):
        """Finish brush stroke"""
        self.is_drawing = False
        
    def add_brush_point(self, x, y):
        """Add brush point as small rectangle"""
        if not self.classes:
            return
            
        size = self.brush_size
        annotation = {
            'type': 'rectangle',
            'class_id': self.selected_class_id,
            'x': max(0, x - size//2),
            'y': max(0, y - size//2),
            'w': size,
            'h': size
        }
        
        self.current_annotations.append(annotation)
        self.display_image()
        
    # ==================== Helper Methods ====================
    
    def find_annotation_at_point(self, x, y):
        """Find annotation at given point"""
        for i, ann in enumerate(self.current_annotations):
            if ann['type'] == 'rectangle':
                if (ann['x'] <= x <= ann['x'] + ann['w'] and 
                    ann['y'] <= y <= ann['y'] + ann['h']):
                    return i
            elif ann['type'] == 'point':
                if abs(ann['x'] - x) <= 10 and abs(ann['y'] - y) <= 10:
                    return i
            elif ann['type'] == 'polygon':
                # Simple point-in-polygon test
                if self.point_in_polygon(x, y, ann['points']):
                    return i
        return None
        
    def point_in_polygon(self, x, y, points):
        """Test if point is inside polygon"""
        n = len(points)
        inside = False
        
        p1x, p1y = points[0]
        for i in range(1, n + 1):
            p2x, p2y = points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
            
        return inside
        
    def display_image_with_temp_annotation(self):
        """Display image with temporary annotation being drawn"""
        if not self.current_image:
            return
            
        # Get display image
        img_width, img_height = self.current_image.size
        display_width = int(img_width * self.zoom_factor)
        display_height = int(img_height * self.zoom_factor)
        
        if self.zoom_factor != 1.0:
            display_image = self.current_image.resize((display_width, display_height), Image.LANCZOS)
        else:
            display_image = self.current_image.copy()
            
        # Draw existing annotations
        if self.current_annotations:
            display_image = self.draw_annotations_on_image(display_image)
            
        # Draw temporary annotation
        draw = ImageDraw.Draw(display_image)
        
        if self.current_bbox and self.annotation_mode == "rectangle":
            x, y, w, h = self.current_bbox
            x = int(x * self.zoom_factor)
            y = int(y * self.zoom_factor)
            w = int(w * self.zoom_factor)
            h = int(h * self.zoom_factor)
            
            class_info = self.get_class_by_id(self.selected_class_id)
            color = class_info['color'] if class_info else '#00FF00'
            draw.rectangle([x, y, x + w, y + h], outline=color, width=2)
            
        elif self.current_polygon_points and self.annotation_mode == "polygon":
            if len(self.current_polygon_points) >= 2:
                scaled_points = []
                for px, py in self.current_polygon_points:
                    scaled_points.extend([int(px * self.zoom_factor), int(py * self.zoom_factor)])
                    
                class_info = self.get_class_by_id(self.selected_class_id)
                color = class_info['color'] if class_info else '#00FF00'
                
                # Draw polygon lines
                for i in range(0, len(scaled_points) - 2, 2):
                    draw.line([scaled_points[i], scaled_points[i+1], 
                              scaled_points[i+2], scaled_points[i+3]], fill=color, width=2)
                    
                # Draw points
                for i in range(0, len(scaled_points), 2):
                    px, py = scaled_points[i], scaled_points[i+1]
                    draw.ellipse([px-3, py-3, px+3, py+3], fill=color, outline='white')
                    
        # Convert to PhotoImage and display
        self.photo_image = ImageTk.PhotoImage(display_image)
        self.canvas.delete("all")
        self.canvas.create_image(self.pan_x, self.pan_y, anchor='nw', image=self.photo_image)
        
    # ==================== Edit Methods ====================
    
    def edit_selected(self):
        """Edit selected annotation"""
        if self.selected_annotation is None:
            messagebox.showwarning("No Selection", "Please select an annotation to edit")
            return
            
        ann = self.current_annotations[self.selected_annotation]
        
        # Show edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Annotation")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Class selection
        ttk.Label(dialog, text="Class:").pack(pady=5)
        class_var = tk.StringVar()
        class_combo = ttk.Combobox(dialog, textvariable=class_var, state='readonly')
        class_combo['values'] = [cls['name'] for cls in self.classes]
        
        # Set current class
        current_class = self.get_class_by_id(ann['class_id'])
        if current_class:
            class_var.set(current_class['name'])
            
        class_combo.pack(pady=5)
        
        # Confidence (if exists)
        conf_frame = ttk.Frame(dialog)
        if 'confidence' in ann:
            conf_frame.pack(pady=5)
            ttk.Label(conf_frame, text="Confidence:").pack(side='left')
            conf_var = tk.DoubleVar(value=ann.get('confidence', 0.5))
            conf_scale = ttk.Scale(conf_frame, from_=0.0, to=1.0, variable=conf_var, orient='horizontal')
            conf_scale.pack(side='left', fill='x', expand=True)
            
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        def save_changes():
            # Find new class ID
            new_class_name = class_var.get()
            new_class_id = None
            for cls in self.classes:
                if cls['name'] == new_class_name:
                    new_class_id = cls['id']
                    break
                    
            if new_class_id is not None:
                ann['class_id'] = new_class_id
                if 'confidence' in ann:
                    ann['confidence'] = conf_var.get()
                    
                self.display_image()
                if self.auto_save:
                    self.save_annotations()
                    
                self.log_message(f"Updated annotation to class: {new_class_name}")
                
            dialog.destroy()
            
        ttk.Button(btn_frame, text="Save", command=save_changes).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)
        
    def delete_selected(self):
        """Delete selected annotation"""
        if self.selected_annotation is not None and 0 <= self.selected_annotation < len(self.current_annotations):
            deleted_ann = self.current_annotations.pop(self.selected_annotation)
            self.selected_annotation = None
            self.display_image()
            self.update_annotation_count()
            
            if self.auto_save:
                self.save_annotations()
                
            class_info = self.get_class_by_id(deleted_ann['class_id'])
            class_name = class_info['name'] if class_info else f"Class_{deleted_ann['class_id']}"
            self.log_message(f"Deleted annotation: {class_name}")
        else:
            messagebox.showwarning("No Selection", "Please select an annotation to delete")
            
    def copy_selected(self):
        """Copy selected annotation"""
        if self.selected_annotation is not None and 0 <= self.selected_annotation < len(self.current_annotations):
            self.copied_annotation = self.current_annotations[self.selected_annotation].copy()
            self.log_message("Annotation copied")
        else:
            messagebox.showwarning("No Selection", "Please select an annotation to copy")
            
    def paste_annotation(self):
        """Paste copied annotation"""
        if not hasattr(self, 'copied_annotation') or self.copied_annotation is None:
            messagebox.showwarning("Nothing to Paste", "No annotation has been copied")
            return
            
        new_annotation = self.copied_annotation.copy()
        
        # Offset the pasted annotation
        if new_annotation['type'] == 'rectangle':
            new_annotation['x'] += 20
            new_annotation['y'] += 20
        elif new_annotation['type'] == 'point':
            new_annotation['x'] += 20
            new_annotation['y'] += 20
        elif new_annotation['type'] == 'polygon':
            new_points = []
            for px, py in new_annotation['points']:
                new_points.append((px + 20, py + 20))
            new_annotation['points'] = new_points
            
        self.current_annotations.append(new_annotation)
        self.display_image()
        self.update_annotation_count()
        
        if self.auto_save:
            self.save_annotations()
            
        self.log_message("Annotation pasted")
        
    def undo_action(self):
        """Undo last action"""
        # Simple undo - remove last annotation
        if self.current_annotations:
            removed = self.current_annotations.pop()
            self.selected_annotation = None
            self.display_image()
            self.update_annotation_count()
            
            if self.auto_save:
                self.save_annotations()
                
            self.log_message("Undid last annotation")
        else:
            messagebox.showinfo("Undo", "Nothing to undo")
            
    def clear_all_annotations(self):
        """Clear all annotations"""
        if self.current_annotations:
            if messagebox.askyesno("Clear All", "Delete all annotations for this image?"):
                self.current_annotations = []
                self.selected_annotation = None
                self.display_image()
                self.update_annotation_count()
                
                if self.auto_save:
                    self.save_annotations()
                    
                self.log_message("Cleared all annotations")
                
    def show_context_menu(self, event):
        """Show context menu"""
        context_menu = tk.Menu(self.root, tearoff=0)
        
        if self.selected_annotation is not None:
            context_menu.add_command(label="Edit Selected", command=self.edit_selected)
            context_menu.add_command(label="Delete Selected", command=self.delete_selected)
            context_menu.add_separator()
            
        context_menu.add_command(label="Paste", command=self.paste_annotation)
        context_menu.add_command(label="Clear All", command=self.clear_all_annotations)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
            
    # ==================== Semi-Automated Methods ====================
    
    def browse_model(self):
        """Browse for model file"""
        file_path = filedialog.askopenfilename(
            title="Select YOLO Model File",
            filetypes=[("PyTorch Model", "*.pt"), ("ONNX Model", "*.onnx"), ("All Files", "*.*")]
        )
        if file_path:
            self.model_path_var.set(file_path)
            
    def load_model(self):
        """Load YOLO model with detailed error reporting"""
        import os
        
        model_path = self.model_path_var.get()
        if not model_path:
            messagebox.showerror("Error", "Please select a model file first")
            return
            
        self.log_message("Loading YOLO model...")
        self.log_message(f"Model path: {model_path}")
        self.update_status("Loading model...")
        
        def load_thread():
            try:
                # Check if file exists
                if not os.path.exists(model_path):
                    self.root.after(0, lambda: self.on_model_load_failed(f"Model file not found: {model_path}"))
                    return
                
                # Check file size
                try:
                    file_size = os.path.getsize(model_path)
                    self.log_message(f"Model file size: {file_size / 1024 / 1024:.2f} MB")
                    
                    if file_size == 0:
                        self.root.after(0, lambda: self.on_model_load_failed("Model file is empty"))
                        return
                        
                    if file_size < 1024:  # Less than 1KB is suspicious
                        self.root.after(0, lambda: self.on_model_load_failed("Model file too small - may be corrupted"))
                        return
                        
                except OSError as e:
                    self.root.after(0, lambda: self.on_model_load_failed(f"Cannot access model file: {e}"))
                    return
                
                # Check if ultralytics is available
                try:
                    from ultralytics import YOLO
                    self.log_message("Ultralytics imported successfully")
                except ImportError as e:
                    self.root.after(0, lambda: self.on_model_load_failed(f"Ultralytics not available: {e}"))
                    return
                
                # Test if file is a valid model by trying to load it directly
                try:
                    test_model = YOLO(model_path)
                    self.log_message("Model file validation successful")
                    del test_model  # Free memory
                except Exception as e:
                    self.root.after(0, lambda: self.on_model_load_failed(f"Invalid model file: {e}"))
                    return
                
                # Now try loading with the engine
                self.log_message("Loading model through AnnotationEngine...")
                success = self.engine.load_model(model_path)
                
                if success:
                    self.root.after(0, self.on_model_loaded)
                else:
                    self.root.after(0, lambda: self.on_model_load_failed("AnnotationEngine failed to load model"))
                    
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                self.log_message(f"Unexpected error details: {error_details}")
                self.root.after(0, lambda: self.on_model_load_failed(f"Unexpected error: {str(e)}"))
                
        threading.Thread(target=load_thread, daemon=True).start()
        
    def on_model_loaded(self):
        """Handle successful model loading"""
        self.log_message("✅ Model loaded successfully!")
        self.update_status("Model loaded - Ready for auto-annotation")
        messagebox.showinfo("Success", "Model loaded successfully!")
        
    def on_model_load_failed(self, error):
        """Handle failed model loading"""
        self.log_message(f"❌ Model loading failed: {error}")
        self.update_status("Model load failed")
        messagebox.showerror("Error", f"Failed to load model: {error}")
        
    def update_confidence(self, value=None):
        """Update confidence threshold"""
        self.confidence_threshold = self.conf_var.get()
        self.conf_label.config(text=f"{self.confidence_threshold:.2f}")
        if hasattr(self.engine, 'set_confidence_threshold'):
            self.engine.set_confidence_threshold(self.confidence_threshold)
            
    def auto_annotate_current(self):
        """Auto-annotate current image"""
        if not self.current_image_path:
            messagebox.showerror("Error", "Please load an image first")
            return
            
        if not hasattr(self.engine, 'model') or self.engine.model is None:
            messagebox.showerror("Error", "Please load a model first")
            return
            
        self.log_message("Running auto-annotation...")
        self.update_status("Auto-annotating...")
        
        try:
            # Run inference
            detections = self.engine.predict(self.current_image_path)
            
            if not detections:
                self.log_message("No objects detected")
                messagebox.showinfo("Auto-Annotation", "No objects detected in current image")
                return
                
            # Convert detections to annotations
            img_width, img_height = self.current_image.size
            added_count = 0
            
            for detection in detections:
                # Convert from x1,y1,x2,y2 to x,y,w,h
                x1, y1, x2, y2 = detection['bbox']
                x = int(x1)
                y = int(y1) 
                w = int(x2 - x1)
                h = int(y2 - y1)
                
                # Find or create matching class
                class_id = self.find_or_create_class(detection['class_name'])
                
                annotation = {
                    'type': 'rectangle',
                    'class_id': class_id,
                    'x': max(0, x),
                    'y': max(0, y),
                    'w': max(1, min(w, img_width - x)),
                    'h': max(1, min(h, img_height - y)),
                    'confidence': detection['confidence']
                }
                
                self.current_annotations.append(annotation)
                added_count += 1
                
            # Update display
            self.display_image()
            self.update_annotation_count()
            
            if self.auto_save:
                self.save_annotations()
                
            self.log_message(f"✅ Added {added_count} auto-annotations")
            self.update_status(f"Auto-annotation complete: {added_count} objects")
            messagebox.showinfo("Success", f"Added {added_count} annotations from AI detection")
            
        except Exception as e:
            self.log_message(f"❌ Auto-annotation failed: {e}")
            messagebox.showerror("Error", f"Auto-annotation failed: {e}")

    def find_or_create_class(self, class_name):
        """Find existing class or create new one"""
        # Look for existing class
        for cls in self.classes:
            if cls['name'].lower() == class_name.lower():
                return cls['id']
                
        # Create new class if not found
        class_id = self.next_class_id
        color = f"#{class_id*50 % 200 + 55:02x}{class_id*80 % 200 + 55:02x}{class_id*120 % 200 + 55:02x}"
        
        new_class = {
            'id': class_id,
            'name': class_name,
            'color': color
        }
        
        self.classes.append(new_class)
        self.next_class_id += 1
        self.update_class_list()
        
        self.log_message(f"Created new class: {class_name}")
        return class_id
        
    def auto_annotate_all(self):
        """Auto-annotate all images with optimized batch processing"""
        if not self.image_list:
            messagebox.showerror("Error", "Please load images first")
            return
            
        if not hasattr(self.engine, 'model') or self.engine.model is None:
            messagebox.showerror("Error", "Please load a model first")
            return
            
        if not messagebox.askyesno("Confirm", f"Auto-annotate all {len(self.image_list)} images?\n"
                                            f"This may take several minutes."):
            return
            
        # Create progress dialog
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Auto-Annotation Progress")
        progress_window.geometry("400x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Center the dialog
        progress_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        ttk.Label(progress_window, text="Processing images...").pack(pady=10)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
        progress_bar.pack(fill='x', padx=20, pady=10)
        
        status_label = ttk.Label(progress_window, text="Preparing...")
        status_label.pack(pady=5)
        
        # Cancel button
        cancelled = {'value': False}
        def cancel_processing():
            cancelled['value'] = True
            progress_window.destroy()
        
        ttk.Button(progress_window, text="Cancel", command=cancel_processing).pack(pady=5)
        
        self.log_message(f"Starting batch auto-annotation of {len(self.image_list)} images...")
    
        def process_batch():
            total_images = len(self.image_list)
            processed_count = 0
            annotation_count = 0
            
            try:
                # Process images in batches for efficiency
                batch_size = 10  # Process 10 images at a time
                
                for i in range(0, total_images, batch_size):
                    if cancelled['value']:
                        break
                        
                    batch_images = self.image_list[i:i + batch_size]
                    
                    # Update progress
                    progress_percent = (processed_count / total_images) * 100
                    self.root.after(0, lambda: [
                        progress_var.set(progress_percent),
                        status_label.config(text=f"Processed {processed_count}/{total_images} images"),
                        progress_window.update()
                    ])
                    
                    # Process batch with YOLO11
                    batch_paths = [str(img_path) for img_path in batch_images]
                    
                    try:
                        # YOLO11 batch inference - much faster than individual predictions
                        results = self.engine.model.predict(batch_paths, 
                                                        conf=self.confidence_threshold, 
                                                        verbose=False,
                                                        save=False,
                                                        show=False)
                        
                        # Process results for each image in the batch
                        for img_path, result in zip(batch_images, results):
                            if cancelled['value']:
                                break
                                
                            processed_count += 1
                            
                            # Parse detections
                            detections = self.parse_single_result(result)
                            
                            if detections:
                                # Convert to annotations and save
                                image_annotations = self.convert_detections_to_annotations(detections, img_path)
                                
                                if image_annotations:
                                    # Save annotations to file
                                    self.save_annotations_for_image(img_path, image_annotations)
                                    annotation_count += len(image_annotations)
                            
                            # Update progress
                            progress_percent = (processed_count / total_images) * 100
                            self.root.after(0, lambda: [
                                progress_var.set(progress_percent),
                                status_label.config(text=f"Processed {processed_count}/{total_images} images"),
                                progress_window.update()
                            ])
                            
                    except Exception as e:
                        self.log_message(f"❌ Batch processing error: {e}")
                        # Continue with next batch
                        continue
                
                progress_window.destroy()
                
                if cancelled['value']:
                    self.log_message("⚠️ Auto-annotation cancelled by user")
                    messagebox.showinfo("Cancelled", "Auto-annotation was cancelled")
                else:
                    self.log_message(f"✅ Batch auto-annotation complete!")
                    self.log_message(f"📊 Processed: {processed_count} images")
                    self.log_message(f"📋 Added: {annotation_count} annotations")
                    
                    # Refresh current image if it was processed
                    if self.current_image_path in self.image_list[:processed_count]:
                        self.load_annotations()
                        self.display_image()
                        self.update_annotation_count()
                    
                    messagebox.showinfo("Complete", 
                                    f"Auto-annotation complete!\n"
                                    f"Processed: {processed_count} images\n"
                                    f"Added: {annotation_count} annotations")
                    
            except Exception as e:
                progress_window.destroy()
                self.log_message(f"❌ Batch processing failed: {e}")
                messagebox.showerror("Error", f"Batch processing failed: {e}")
        
        # Run processing in a separate thread to prevent UI freezing
        import threading
        threading.Thread(target=process_batch, daemon=True).start()

    def parse_single_result(self, result):
        """Parse single YOLO result"""
        detections = []
        
        if result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()  # x1, y1, x2, y2
            confidences = result.boxes.conf.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy().astype(int)
            
            for box, conf, cls in zip(boxes, confidences, classes):
                x1, y1, x2, y2 = box
                detection = {
                    'class_id': int(cls),
                    'class_name': self.engine.class_names[cls] if cls < len(self.engine.class_names) else f"class_{cls}",
                    'confidence': float(conf),
                    'bbox': [float(x1), float(y1), float(x2), float(y2)]
                }
                detections.append(detection)
                
        return detections

    def convert_detections_to_annotations(self, detections, img_path):
        """Convert detections to annotation format"""
        try:
            # Get image dimensions
            from PIL import Image
            with Image.open(img_path) as img:
                img_width, img_height = img.size
            
            annotations = []
            
            for detection in detections:
                # Convert from x1,y1,x2,y2 to x,y,w,h
                x1, y1, x2, y2 = detection['bbox']
                x = int(x1)
                y = int(y1)
                w = int(x2 - x1)
                h = int(y2 - y1)
                
                # Find or create matching class
                class_id = self.find_or_create_class(detection['class_name'])
                
                annotation = {
                    'type': 'rectangle',
                    'class_id': class_id,
                    'x': max(0, x),
                    'y': max(0, y),
                    'w': max(1, min(w, img_width - x)),
                    'h': max(1, min(h, img_height - y)),
                    'confidence': detection['confidence']
                }
                
                annotations.append(annotation)
                
            return annotations
            
        except Exception as e:
            self.log_message(f"❌ Error converting detections for {img_path.name}: {e}")
            return []

    def save_annotations_for_image(self, img_path, annotations):
        """Save annotations for specific image"""
        try:
            # Create annotations folder
            image_folder = img_path.parent
            annotations_folder = image_folder / "annotations"
            annotations_folder.mkdir(exist_ok=True)
            
            # Save annotation file
            annotation_filename = img_path.stem + '.txt'
            annotation_path = annotations_folder / annotation_filename
            
            # Get image dimensions
            from PIL import Image
            with Image.open(img_path) as img:
                img_width, img_height = img.size
            
            with open(annotation_path, 'w') as f:
                for ann in annotations:
                    if ann['type'] == 'rectangle':
                        # Convert to YOLO format
                        x_center = (ann['x'] + ann['w']/2) / img_width
                        y_center = (ann['y'] + ann['h']/2) / img_height
                        width = ann['w'] / img_width
                        height = ann['h'] / img_height
                        
                        line = f"{ann['class_id']} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
                        
                        # FIXED: Check the checkbox before including confidence
                        if 'confidence' in ann and self.include_confidence_var.get():
                            line += f" {ann['confidence']:.6f}"
                            
                        f.write(line + '\n')
                        
        except Exception as e:
            self.log_message(f"Error saving annotations for {img_path.name}: {e}")
        
    def smart_suggestions(self):
        """Get smart annotation suggestions"""
        messagebox.showinfo("Smart Suggestions", "AI-powered suggestions feature coming soon!")
        
    # ==================== Export Methods ====================
    
    def update_split_ratios(self, value=None):
        """Update train/val split ratios"""
        # Round to avoid floating point precision issues
        train_ratio = round(self.train_var.get(), 2)
        val_ratio = round(1.0 - train_ratio, 2)
        
        # Update instance variables
        self.train_split = train_ratio
        self.val_split = val_ratio
        
        # Update display labels with proper rounding
        train_percent = round(train_ratio * 100)
        val_percent = round(val_ratio * 100)
        
        self.train_label.config(text=f"{train_percent}%")
        self.val_label.config(text=f"{val_percent}%")
        
    def save_all_annotations(self):
        """Save all annotations"""
        if not self.image_list:
            messagebox.showwarning("No Images", "Please load images first")
            return
            
        saved_count = 0
        current_index = self.current_image_index
        
        for i, img_path in enumerate(self.image_list):
            self.current_image_index = i
            self.current_image_path = img_path
            
            try:
                self.current_image = Image.open(img_path)
                if self.current_image.mode != 'RGB':
                    self.current_image = self.current_image.convert('RGB')
                    
                self.load_annotations()
                if self.current_annotations:
                    self.save_annotations()
                    saved_count += 1
            except Exception as e:
                self.log_message(f"Error processing {img_path.name}: {e}")
                
        # Restore original position
        self.current_image_index = current_index
        self.load_current_image()
        
        self.log_message(f"Saved annotations for {saved_count} images")
        messagebox.showinfo("Save Complete", f"Saved annotations for {saved_count} images")

    def save_project(self):
        """Save current project to file"""
        if not self.image_list:
            messagebox.showwarning("No Project", "No images loaded to save as project")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Project",
            defaultextension=".anno",
            filetypes=[("Annotation Project", "*.anno"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            # Save current annotations first
            if self.current_annotations and self.auto_save:
                self.save_annotations()
                
            project_data = {
                "project_name": Path(file_path).stem,
                "created_date": datetime.now().isoformat(),
                "tool_version": "2.1",
                "image_folder": str(self.image_list[0].parent) if self.image_list else "",
                "image_list": [str(img) for img in self.image_list],
                "classes": self.classes,
                "selected_class_id": self.selected_class_id,
                "next_class_id": self.next_class_id,
                "settings": {
                    "confidence_threshold": self.confidence_threshold,
                    "auto_save": self.auto_save,
                    "brush_size": self.brush_size,
                    "show_labels": self.show_labels,
                    "show_confidence": self.show_confidence,
                    "export_format": self.export_format,
                    "train_split": self.train_split,
                    "val_split": self.val_split
                },
                "current_image_index": self.current_image_index,
                "annotation_mode": self.annotation_mode,
                "zoom_factor": self.zoom_factor
            }
            
            with open(file_path, 'w') as f:
                json.dump(project_data, f, indent=2)
                
            self.log_message(f"✅ Project saved: {Path(file_path).name}")
            self.update_status(f"Project saved: {Path(file_path).name}")
            messagebox.showinfo("Success", f"Project saved successfully!\n{file_path}")
            
        except Exception as e:
            self.log_message(f"❌ Error saving project: {e}")
            messagebox.showerror("Error", f"Failed to save project: {e}")

    def load_project(self):
        """Load project from file"""
        file_path = filedialog.askopenfilename(
            title="Load Project",
            filetypes=[("Annotation Project", "*.anno"), ("All files", "*.*")]
        )

        if not file_path:
            return
            
        try:
            with open(file_path, 'r') as f:
                project_data = json.load(f)
                
            # Validate project data
            required_keys = ["image_list", "classes"]
            if not all(key in project_data for key in required_keys):
                raise ValueError("Invalid project file format")
                
            # Load image list
            image_paths = [Path(img_path) for img_path in project_data["image_list"]]
            # Filter out non-existent images
            existing_images = [img for img in image_paths if img.exists()]
            
            if not existing_images:
                messagebox.showwarning("No Images Found", 
                                    "None of the images in this project could be found.\n"
                                    "They may have been moved or deleted.")
                return
                
            if len(existing_images) != len(image_paths):
                missing_count = len(image_paths) - len(existing_images)
                if not messagebox.askyesno("Missing Images", 
                                        f"{missing_count} images from this project are missing.\n"
                                        f"Load project with {len(existing_images)} available images?"):
                    return
                    
            # Load project data
            self.image_list = existing_images
            self.classes = project_data["classes"]
            self.selected_class_id = project_data.get("selected_class_id", 0)
            self.next_class_id = project_data.get("next_class_id", len(self.classes))
            
            # Load settings if available - WITH ERROR HANDLING
            if "settings" in project_data:
                settings = project_data["settings"]
                self.confidence_threshold = settings.get("confidence_threshold", 0.5)
                self.auto_save = settings.get("auto_save", True)
                self.brush_size = settings.get("brush_size", 3)
                self.show_labels = settings.get("show_labels", True)
                self.show_confidence = settings.get("show_confidence", True)
                self.export_format = settings.get("export_format", "YOLO11")
                self.train_split = settings.get("train_split", 0.8)
                self.val_split = settings.get("val_split", 0.2)
                
                # Update UI elements with loaded settings - SAFE UPDATES
                if hasattr(self, 'conf_var'):
                    self.conf_var.set(self.confidence_threshold)
                
                # REMOVED: self.brush_var.set(self.brush_size) - this doesn't exist
                
                if hasattr(self, 'show_labels_var'):
                    self.show_labels_var.set(self.show_labels)
                
                if hasattr(self, 'show_conf_var'):
                    self.show_conf_var.set(self.show_confidence)
                
                if hasattr(self, 'export_format_var'):
                    self.export_format_var.set(self.export_format)
                
                if hasattr(self, 'train_var'):
                    self.train_var.set(self.train_split)
                    
            # Load view settings
            self.annotation_mode = project_data.get("annotation_mode", "rectangle")
            self.zoom_factor = project_data.get("zoom_factor", 1.0)
            
            # Load current image
            self.current_image_index = project_data.get("current_image_index", 0)
            if self.current_image_index >= len(self.image_list):
                self.current_image_index = 0
                
            # Update UI
            self.update_image_listbox()
            self.update_class_list()
            self.set_annotation_mode(self.annotation_mode)
            self.load_current_image()
            self.update_image_counter()
            
            # Safe UI updates
            if hasattr(self, 'update_split_ratios'):
                self.update_split_ratios()
            if hasattr(self, 'update_confidence'):
                self.update_confidence()
            
            project_name = project_data.get("project_name", Path(file_path).stem)
            tool_version = project_data.get("tool_version", "Unknown")
            self.root.title(f"Annotex v2.1 - {project_name}")
            
            self.log_message(f"✅ Project loaded: {project_name}")
            self.log_message(f"📁 Images: {len(self.image_list)}")
            self.log_message(f"🏷️ Classes: {len(self.classes)}")
            self.log_message(f"🔧 Tool version: {tool_version}")
            self.update_status(f"Project loaded: {project_name}")
            
            messagebox.showinfo("Success", f"Project loaded successfully!\n"
                            f"Images: {len(self.image_list)}\n"
                            f"Classes: {len(self.classes)}")
            
        except Exception as e:
            self.log_message(f"❌ Error loading project: {e}")
            messagebox.showerror("Error", f"Failed to load project: {e}")

    def new_project(self):
        """Start a new project"""
        if self.image_list or self.current_annotations:
            if not messagebox.askyesno("New Project", 
                                    "This will clear the current project.\n"
                                    "Continue?"):
                return
                
        # Reset everything
        self.image_list = []
        self.current_image = None
        self.current_image_path = None
        self.original_image = None
        self.current_annotations = []
        self.selected_annotation = None
        self.current_image_index = 0
        
        # Reset view state
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        
        # Class management - Dynamic classes
        self.classes = [] 
        self.selected_class_id = 0
        self.next_class_id = 0
        
        # Reset settings to defaults
        self.confidence_threshold = 0.5
        self.auto_save = True
        self.brush_size = 3
        self.show_labels = True
        self.show_confidence = True
        self.export_format = "YOLO11"
        self.train_split = 0.8
        self.val_split = 0.2
        self.annotation_mode = "rectangle"
        
        # Update UI with reset values
        self.conf_var.set(self.confidence_threshold)
        self.brush_var.set(self.brush_size)
        self.show_labels_var.set(self.show_labels)
        self.show_conf_var.set(self.show_confidence)
        self.export_format_var.set(self.export_format)
        self.train_var.set(self.train_split)
        
        # Clear UI
        self.canvas.delete("all")
        self.image_listbox.delete(0, tk.END)
        self.update_class_list()
        self.update_image_counter()
        self.update_annotation_count()
        self.update_split_ratios()
        self.set_annotation_mode("rectangle")
        
        self.root.title("Annotex v2.1")
        self.log_message("🆕 New project started")
        self.update_status("New project - Load images to start")
            
    def export_dataset(self):
        """Export dataset in YOLO format"""
        if not self.image_list:
            messagebox.showwarning("No Images", "Please load images first")
            return
            
        # Save current image annotations first
        if self.current_annotations and self.current_image_path:
            self.save_annotations()
            self.log_message("💾 Saved current annotations before export")
            
        # Select output directory
        output_dir = filedialog.askdirectory(title="Select Export Directory")
        if not output_dir:
            return
            
        self.log_message(f"Exporting dataset to: {output_dir}")
        
        try:
            self.create_yolo_dataset(output_dir)
            messagebox.showinfo("Export Complete", f"Dataset exported to:\n{output_dir}")
            self.log_message("✅ Dataset export completed!")
        except Exception as e:
            self.log_message(f"❌ Export failed: {e}")
            messagebox.showerror("Export Error", f"Export failed: {e}")


    def create_yolo_dataset(self, output_dir):
        """Create YOLO format dataset"""
        output_path = Path(output_dir)
        
        # Create directory structure
        train_images_dir = output_path / "train" / "images"
        train_labels_dir = output_path / "train" / "labels"
        val_images_dir = output_path / "val" / "images"
        val_labels_dir = output_path / "val" / "labels"
        
        for dir_path in [train_images_dir, train_labels_dir, val_images_dir, val_labels_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        # Get annotated images - check both locations
        annotated_images = []
        
        for img_path in self.image_list:
            annotation_found = False
            
            # Check in annotations subfolder (new location)
            image_folder = img_path.parent
            annotations_folder = image_folder / "annotations"
            annotation_filename = img_path.stem + '.txt'
            ann_path_new = annotations_folder / annotation_filename
            
            # Check in same folder as image (old location)
            ann_path_old = img_path.with_suffix('.txt')
            
            if ann_path_new.exists():
                annotated_images.append((img_path, ann_path_new))
                annotation_found = True
            elif ann_path_old.exists():
                annotated_images.append((img_path, ann_path_old))
                annotation_found = True
                
            # Debug logging
            if annotation_found:
                self.log_message(f"✓ Found annotations for: {img_path.name}")
            else:
                self.log_message(f"✗ No annotations for: {img_path.name}")
                
        if not annotated_images:
            # More detailed error message
            self.log_message("❌ No annotated images found!")
            self.log_message(f"🔍 Checked {len(self.image_list)} images")
            self.log_message("💡 Make sure to save annotations before exporting")
            raise ValueError(f"No annotated images found. Checked {len(self.image_list)} images.\n"
                            f"Make sure annotations are saved before exporting.")
            
        self.log_message(f"📋 Found {len(annotated_images)} annotated images")
            
        # Split dataset
        import random
        random.shuffle(annotated_images)
        
        train_split = self.train_var.get()
        split_index = int(len(annotated_images) * train_split)
        
        train_images = annotated_images[:split_index]
        val_images = annotated_images[split_index:]
        
        # Copy files with confidence processing
        def copy_dataset(image_ann_pairs, img_dir, lbl_dir):
            for img_path, ann_path in image_ann_pairs:
                # Copy image
                shutil.copy2(img_path, img_dir / img_path.name)
                
                # Process annotation file based on confidence setting
                self.process_annotation_file(ann_path, lbl_dir / (img_path.stem + '.txt'))
                    
        copy_dataset(train_images, train_images_dir, train_labels_dir)
        copy_dataset(val_images, val_images_dir, val_labels_dir)
        
        self.log_message(f"📤 Exported {len(train_images)} training images")
        self.log_message(f"📤 Exported {len(val_images)} validation images")
        
        # Create data.yaml if requested
        if self.create_yaml_var.get():
            self.create_data_yaml(output_path)

    def process_annotation_file(self, source_path, target_path):
        """Process annotation file and optionally remove confidence scores"""
        try:
            with open(source_path, 'r') as f:
                lines = f.readlines()
            
            with open(target_path, 'w') as f:
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        if self.include_confidence_var.get() and len(parts) == 6:
                            # Keep all 6 values (including confidence)
                            f.write(line)
                        else:
                            # Keep only first 5 values (remove confidence)
                            clean_line = ' '.join(parts[:5]) + '\n'
                            f.write(clean_line)
                            
        except Exception as e:
            self.log_message(f"Error processing annotation file {source_path}: {e}")
            
    def create_data_yaml(self, output_path):
        """Create data.yaml file for YOLO training"""
        data_yaml = {
            'train': str(output_path / 'train' / 'images'),
            'val': str(output_path / 'val' / 'images'),
            'nc': len(self.classes),
            'names': [cls['name'] for cls in self.classes]
        }
        
        with open(output_path / 'data.yaml', 'w') as f:
            yaml.dump(data_yaml, f, default_flow_style=False)
            
        self.log_message("Created data.yaml file")

    def add_individual_images(self):
        """Add individual image files"""
        files = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
        )
        
        if files:
            new_images = [Path(f) for f in files]
            
            # Add to existing list or create new
            if not hasattr(self, 'image_list') or not self.image_list:
                self.image_list = []
                
            self.image_list.extend(new_images)
            self.image_list = list(set(self.image_list))  # Remove duplicates
            self.image_list.sort()
            
            # Update image listbox
            self.update_image_listbox()
            
            if not hasattr(self, 'current_image_index'):
                self.current_image_index = 0
                self.load_current_image()
                
            self.log_message(f"Added {len(new_images)} images")

    def update_image_listbox(self):
        """Update image listbox display"""
        self.image_listbox.delete(0, tk.END)
        for img_path in self.image_list:
            ann_path = img_path.with_suffix('.txt')
            status = "✓" if ann_path.exists() else "○"
            self.image_listbox.insert(tk.END, f"{status} {img_path.name}")
        self.update_image_counter()

    def remove_selected_image(self):
        """Remove selected image from list"""
        selection = self.image_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an image to remove")
            return
            
        if messagebox.askyesno("Confirm", "Remove selected image from list?"):
            idx = selection[0]
            removed_img = self.image_list.pop(idx)
            
            # Adjust current index if needed
            if idx <= self.current_image_index and self.current_image_index > 0:
                self.current_image_index -= 1
            elif idx == self.current_image_index and idx >= len(self.image_list):
                self.current_image_index = len(self.image_list) - 1
                
            self.update_image_listbox()
            
            if self.image_list:
                self.load_current_image()
            else:
                self.current_image = None
                self.current_image_path = None
                self.canvas.delete("all")
                
            self.log_message(f"Removed: {removed_img.name}")

    def clear_all_images(self):
        """Clear all images from list"""
        if self.image_list and messagebox.askyesno("Confirm", "Clear all images from list?"):
            self.image_list = []
            self.current_image = None
            self.current_image_path = None
            self.current_annotations = []
            self.canvas.delete("all")
            self.image_listbox.delete(0, tk.END)
            self.update_image_counter()
            self.update_annotation_count()
            self.log_message("Cleared all images")    


# ============================================================================
# Main Application Entry Point
# ============================================================================

def main():
    """Main application entry point"""
    root = tk.Tk()
    
    # Set application icon (if available)
    try:
        # root.iconbitmap('icon.ico')
        pass
    except:
        pass
    
    # Create and run the application
    app = Annotex(root)
    
    # Handle window closing
    def on_closing():
        if app.current_annotations and app.auto_save:
            app.save_annotations()
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()