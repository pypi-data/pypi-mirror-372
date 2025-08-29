# Annotex 🚀

**AI-Powered Annotation Tool for Computer Vision Datasets**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
<!-- [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) -->
<!-- [![PyPI version](https://badge.fury.io/py/annotex.svg)](https://badge.fury.io/py/annotex) -->
<!-- [![Downloads](https://pepy.tech/badge/annotex)](https://pepy.tech/project/annotex) -->

Annotex is a professional-grade annotation tool designed for creating high-quality computer vision datasets. With AI-powered assistance and an intuitive interface, it streamlines the annotation process for machine learning practitioners.

![Annotex Interface](assets/screenshots/main_interface.png)

## ✨ Features

### 🎯 **Professional Annotation Tools**
- **Rectangle Annotation** - Precise bounding box creation
- **AI-Assisted Annotation** - Auto-annotation with pre-trained YOLO models
- **Batch Processing** - Process multiple images simultaneously

### 🔧 **Advanced Workflow**
- **Project Management** - Save/load projects (.anno format)
- **Class Management** - Dynamic class creation with custom colors
- **Export Formats** - YOLO11, YOLOv8, compatible
- **Quality Control** - Confidence scoring and validation

### 🚀 **Performance Optimized**
- **Memory Efficient** - Handles large datasets smoothly
- **Real-time Preview** - Instant annotation feedback
- **Keyboard Shortcuts** - Professional workflow acceleration

## 📦 Installation

### Quick Install
```bash
pip install annotex
```

## 🚀 Quick Start

### Launch Annotex
```bash
# Start the GUI
annotex

# Or
python -m annotex.main

# Load a project
annotex --project my_project.anno

# Load images from directory
annotex --images /path/to/images
```

### Basic Workflow
1. **Load Images** - Import your image dataset
2. **Create Classes** - Define annotation classes
3. **Annotate** - Create bounding boxes manually or with AI
4. **Export** - Generate YOLO-format dataset

## 📚 Documentation

### Keyboard Shortcuts

| Category | Shortcut | Action |
|----------|----------|--------|
| **Navigation** | `Left Arrow` | Previous image |
| | `Right Arrow` | Next image |
| | `Home` | First image |
| | `End` | Last image |
| | `Ctrl + +` | Zoom in |
| | `Ctrl + -` | Zoom out |
| | `Ctrl + 0` | Zoom fit |
| | `Ctrl + R` | Reset view |
| **File Operations** | `Ctrl + N` | New project |
| | `Ctrl + O` | Open project |
| | `Ctrl + S` | Save current |
| | `Ctrl + Shift + S` | Save project |
| | `Ctrl + I` | Load images |
| | `Ctrl + E` | Export dataset |
| **Editing** | `Ctrl + Z` | Undo |
| | `Ctrl + C` | Copy annotation |
| | `Ctrl + V` | Paste annotation |
| | `Delete` | Delete selected |
| | `Ctrl + Shift + C` | Clear all |
| | `R` | Rectangle tool |
| **Tools & Classes** | `1-9` | Select class by number |
| | `F1` | Show shortcuts |
| | `Middle Click + Drag` | Pan image |
| | `Mouse Wheel` | Zoom in/out |
| | `Right Click` | Context menu |

## 🎨 Interface Overview

### Main Components
- **Tools Panel** - Annotation tools and class management
- **Image Viewer** - Zoomable canvas with annotation overlay
- **Image List** - Project image management
- **Export Panel** - Dataset export configuration

### Advanced Features
- **Semi-Automated Annotation** - Pre-trained AI model integration
- **Batch Processing** - Multi-image operations
- **Quality Metrics** - Annotation statistics and validation
- **Custom Export** - Flexible dataset formats (Currently:only YOLO formats)

## 🤖 AI Integration

### Supported Models
- **YOLO11** - Proven performance
- **Custom Models** - Load your own trained models

### Auto-Annotation Workflow
```bash
1. Load pre-trained model (.pt file)
2. Set confidence threshold
3. Run individual or batch annotation
4. Review and refine results
5. Export final dataset

Possible Usage: Pre-train your AI model on a small dataset and use that model to annotate the rest of the dataset.
```

## 🏗️ Roadmap

### Version 2.2 (Coming Soon)
- [ ] Polygon annotation tool
- [ ] Point annotation support
- [ ] Brush/segmentation tool
- [ ] COCO format export
- [ ] Pascal VOC format support

### Version 2.3 (Planned)
<!-- - [ ] Cloud storage integration -->
- [ ] Team collaboration features
- [ ] Advanced AI suggestions
<!-- - [ ] Mobile app companion -->

## 📞 Support

- 📧 **Email**: randikamk.96@gmail.com

## 🌟 Acknowledgments

- [Ultralytics](https://ultralytics.com/) for YOLO implementation
- [OpenCV](https://opencv.org/) for computer vision tools
- [Tkinter](https://docs.python.org/3/library/tkinter.html) for GUI framework

---

**⭐ Star us on GitHub if Annotex helps your projects!**

Made by [Randika](https://github.com/RandikaKM)