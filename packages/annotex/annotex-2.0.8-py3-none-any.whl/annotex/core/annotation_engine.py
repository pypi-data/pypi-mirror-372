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