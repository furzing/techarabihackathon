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
import os
import logging
from datetime import datetime, timedelta
from models import *
from llm import Groq_Env, SocialMediaManager

from config import config
from gemini_service import GeminiService
from image_processor import ImageProcessor
from models import AnalysisResponse, AnalysisData, VersionComparisonRequest


# Configure logging - Saad
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Design Version Control AI and Analysis API and Social Media Manager",
    description="AI-powered design comparison and analysis service and AI-powered Social Media Management & Automation API",
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
try:
    groq_env = Groq_Env()
    smm = SocialMediaManager(groq_env)
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    raise

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "مرحباً بك في API إدارة وسائل التواصل الاجتماعي و تحليل التصميمات",
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


@app.post("/api/strategy", response_model=APIResponse)
async def generate_strategy(request: StrategyRequest):
    """
    Generate a comprehensive social media strategy for a business
    """
    try:
        logger.info(f"Generating strategy for business: {request.business_info.business_name}")
        strategy = smm.generate_strategy(request.business_info)
        
        return APIResponse(
            success=True,
            data=strategy,
            message="تم إنشاء الاستراتيجية بنجاح"
        )
    except Exception as e:
        logger.error(f"Error generating strategy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطأ في إنشاء الاستراتيجية: {str(e)}"
        )

@app.post("/api/marketing-plan", response_model=APIResponse)
async def create_marketing_plan(request: MarketingPlanRequest):
    """
    Create a detailed marketing plan based on strategy
    """
    try:
        logger.info(f"Creating marketing plan for duration: {request.duration}")
        plan = smm.create_marketing_plan(request.strategy, request.duration)
        
        return APIResponse(
            success=True,
            data=plan,
            message="تم إنشاء الخطة التسويقية بنجاح"
        )
    except Exception as e:
        logger.error(f"Error creating marketing plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطأ في إنشاء الخطة التسويقية: {str(e)}"
        )

@app.post("/api/content-suggestions", response_model=APIResponse)
async def suggest_content(request: ContentSuggestionRequest):
    """
    Generate content suggestions for a specific topic
    """
    try:
        logger.info(f"Generating content suggestions for topic: {request.topic}")
        suggestions = smm.suggest_content(
            request.topic, 
            request.content_type, 
            request.target_platform
        )
        
        return APIResponse(
            success=True,
            data=suggestions,
            message="تم إنشاء اقتراحات المحتوى بنجاح"
        )
    except Exception as e:
        logger.error(f"Error generating content suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطأ في إنشاء اقتراحات المحتوى: {str(e)}"
        )

@app.post("/api/create-post", response_model=APIResponse)
async def create_post(request: PostCreationRequest):
    """
    Create a ready-to-publish social media post
    """
    try:
        logger.info(f"Creating post for platform: {request.platform}")
        post = smm.create_post(request.idea, request.platform, request.tone)
        
        return APIResponse(
            success=True,
            data=post,
            message="تم إنشاء المنشور بنجاح"
        )
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطأ في إنشاء المنشور: {str(e)}"
        )

@app.post("/api/schedule-post", response_model=APIResponse)
async def schedule_post(request: PostScheduleRequest):
    """
    Schedule a post for future publication
    """
    try:
        logger.info(f"Scheduling post for date: {request.scheduled_date}")
        
        # Validate that the scheduled date is in the future
        if request.scheduled_date <= datetime.now().date():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="تاريخ الجدولة يجب أن يكون في المستقبل"
            )
        
        # Mock scheduling (in real implementation, you'd integrate with actual scheduling service)
        scheduled_info = f"تم جدولة المنشور بنجاح ليوم {request.scheduled_date}\n\nمحتوى المنشور: {request.post_content[:100]}..."
        
        return APIResponse(
            success=True,
            data=scheduled_info,
            message="تم جدولة المنشور بنجاح"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطأ في جدولة المنشور: {str(e)}"
        )

@app.post("/api/moderate-post", response_model=APIResponse)
async def moderate_post(request: PostModerationRequest):
    """
    Analyze and moderate post content for compliance
    """
    try:
        logger.info("Moderating post content")
        moderation_result = smm.moderate_post(request.post_content)
        
        return APIResponse(
            success=True,
            data=moderation_result,
            message="تم تحليل المحتوى بنجاح"
        )
    except Exception as e:
        logger.error(f"Error moderating post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطأ في تحليل المحتوى: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "الخدمة تعمل بشكل طبيعي"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "حدث خطأ غير متوقع في الخادم",
            "detail": str(exc)
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=True  # Set to False in production
    )