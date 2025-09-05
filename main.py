from fastapi import *
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional
import asyncio
import aiofiles
import io
from PIL import Image
import requests

from config import config
from gemini_service import GeminiService
from image_processor import ImageProcessor
from models import AnalysisResponse, AnalysisData, VersionComparisonRequest

app = FastAPI(
    title="Design Version Control AI",
    description="AI-powered design comparison and analysis service",
    version="1.0.0"
)

# Configure CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
gemini_service = GeminiService()
image_processor = ImageProcessor()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "active",
        "service": "Design Version AI",
        "endpoints": [
            "/analyze - Compare two design versions",
            "/analyze-urls - Compare designs from URLs",
            "/rate-limit - Check API rate limit status"
        ]
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_designs(
    version1: UploadFile = File(..., description="First design version (older)"),
    version2: UploadFile = File(..., description="Second design version (newer)"),
    context: Optional[str] = Body(None, description="Additional context about the design")
):
    """
    Analyze differences between two design versions uploaded as files.
    
    Returns detailed analysis including changes, suggestions, and auto-generated comments.
    """
    try:
        # Read and validate images
        image1_bytes = await version1.read()
        image2_bytes = await version2.read()
        
        # Validate first image
        is_valid, error = image_processor.validate_image(
            image1_bytes, 
            config.MAX_IMAGE_SIZE, 
            config.ALLOWED_EXTENSIONS
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Version 1 validation failed: {error}")
        
        # Validate second image
        is_valid, error = image_processor.validate_image(
            image2_bytes, 
            config.MAX_IMAGE_SIZE, 
            config.ALLOWED_EXTENSIONS
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Version 2 validation failed: {error}")
        
        # Resize if needed for optimization
        image1_bytes = image_processor.resize_image_if_needed(image1_bytes)
        image2_bytes = image_processor.resize_image_if_needed(image2_bytes)
        
        # Prepare images for Gemini
        img1 = image_processor.prepare_image_for_gemini(image1_bytes)
        img2 = image_processor.prepare_image_for_gemini(image2_bytes)
        
        # Analyze with Gemini
        result = await gemini_service.analyze_design_changes(img1, img2, context)
        
        if not result.success:
            raise HTTPException(status_code=503, detail=result.error)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/analyze-urls", response_model=AnalysisResponse)
async def analyze_designs_from_urls(request: VersionComparisonRequest):
    """
    Analyze differences between two design versions from URLs.
    
    Useful when designs are already hosted somewhere.
    """
    try:
        if not request.version1_url or not request.version2_url:
            raise HTTPException(status_code=400, detail="Both version URLs are required")
        
        # Download images
        response1 = requests.get(request.version1_url, timeout=30)
        response2 = requests.get(request.version2_url, timeout=30)
        
        if response1.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download version 1")
        if response2.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download version 2")
        
        image1_bytes = response1.content
        image2_bytes = response2.content
        
        # Validate and process
        is_valid, error = image_processor.validate_image(
            image1_bytes, 
            config.MAX_IMAGE_SIZE, 
            config.ALLOWED_EXTENSIONS
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Version 1 validation failed: {error}")
        
        is_valid, error = image_processor.validate_image(
            image2_bytes, 
            config.MAX_IMAGE_SIZE, 
            config.ALLOWED_EXTENSIONS
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Version 2 validation failed: {error}")
        
        # Resize if needed
        image1_bytes = image_processor.resize_image_if_needed(image1_bytes)
        image2_bytes = image_processor.resize_image_if_needed(image2_bytes)
        
        # Prepare images
        img1 = image_processor.prepare_image_for_gemini(image1_bytes)
        img2 = image_processor.prepare_image_for_gemini(image2_bytes)
        
        # Analyze
        result = await gemini_service.analyze_design_changes(img1, img2, request.context)
        
        if not result.success:
            raise HTTPException(status_code=503, detail=result.error)
        
        return result
        
    except HTTPException:
        raise
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to download images: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/rate-limit")
async def get_rate_limit_status():
    """
    Check current API rate limit status.
    
    Useful for the frontend to show remaining requests.
    """
    return gemini_service.get_rate_limit_status()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=True  # Set to False in production
    )