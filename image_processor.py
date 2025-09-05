from PIL import Image
import io
import base64
from typing import Tuple, Optional
import hashlib

class ImageProcessor:
    @staticmethod
    def validate_image(image_bytes: bytes, max_size: int, allowed_extensions: list) -> Tuple[bool, Optional[str]]:
        """Validate image size and format"""
        if len(image_bytes) > max_size:
            return False, f"Image size exceeds {max_size/1024/1024:.1f}MB limit"
        
        try:
            img = Image.open(io.BytesIO(image_bytes))
            format = img.format.lower()
            if format not in [ext.lower() for ext in allowed_extensions]:
                return False, f"Image format {format} not allowed"
            return True, None
        except Exception as e:
            return False, f"Invalid image: {str(e)}"
    
    @staticmethod
    def resize_image_if_needed(image_bytes: bytes, max_dimension: int = 1024) -> bytes:
        """Resize image if it's too large for efficient processing"""
        img = Image.open(io.BytesIO(image_bytes))
        
        if max(img.size) > max_dimension:
            ratio = max_dimension / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            img.save(output, format=img.format or 'PNG')
            return output.getvalue()
        
        return image_bytes
    
    @staticmethod
    def calculate_image_hash(image_bytes: bytes) -> str:
        """Calculate hash for image caching"""
        return hashlib.md5(image_bytes).hexdigest()
    
    @staticmethod
    def prepare_image_for_gemini(image_bytes: bytes) -> Image.Image:
        """Prepare image for Gemini API"""
        return Image.open(io.BytesIO(image_bytes))