from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from datetime import datetime, timedelta
from models import *
from llm import Groq_Env, SocialMediaManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Social Media Manager API",
    description="AI-powered Social Media Management & Automation API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    groq_env = Groq_Env()
    smm = SocialMediaManager(groq_env)
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    raise

@app.get("/")
async def root():
    return {"message": "مرحباً بك في API إدارة وسائل التواصل الاجتماعي", "status": "متصل"}

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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
