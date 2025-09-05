import google.generativeai as genai
from typing import List, Dict, Optional, Tuple
from PIL import Image
import json
import asyncio
from datetime import datetime, timedelta
from config import config
from models import DesignChange, AnalysisResponse, AnalysisData

class GeminiService:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.request_times = []
        self.daily_requests = 0
        self.last_reset = datetime.now()
    
    def _check_rate_limit(self) -> Tuple[bool, Optional[str]]:
        """Check if we're within rate limits"""
        now = datetime.now()
        
        # Reset daily counter if needed
        if (now - self.last_reset).days >= 1:
            self.daily_requests = 0
            self.last_reset = now
        
        # Check daily limit
        if self.daily_requests >= config.REQUESTS_PER_DAY:
            return False, "Daily API limit reached. Please try again tomorrow."
        
        # Check per-minute limit
        minute_ago = now - timedelta(minutes=1)
        self.request_times = [t for t in self.request_times if t > minute_ago]
        
        if len(self.request_times) >= config.REQUESTS_PER_MINUTE:
            return False, "Rate limit exceeded. Please wait a minute."
        
        return True, None
    
    async def analyze_design_changes(
        self, 
        image1: Image.Image, 
        image2: Image.Image,
        context: Optional[str] = None
    ) -> AnalysisResponse:
        """Analyze differences between two design versions"""
        
        # Check rate limits
        can_proceed, error_msg = self._check_rate_limit()
        if not can_proceed:
            return AnalysisResponse(
                success=False,
                timestamp=datetime.now(),
                data=AnalysisData(
                    similarity_score=0,
                    summary_en="",
                    summary_ar="",
                    changes_detected=[],
                    designer_notes_en=[],
                    designer_notes_ar=[],
                    next_steps_en=[],
                    next_steps_ar=[]
                ),
                error=error_msg
            )
        
        # Update rate limit tracking
        self.request_times.append(datetime.now())
        self.daily_requests += 1
        
        # Direct design feedback prompt for team collaboration
        prompt = f"""You are a senior design lead providing direct feedback to your design team. 
        
        Analyze these two design versions (Version 1 = old, Version 2 = new) and provide ACTIONABLE feedback.
        
        IMPORTANT: Focus on WHAT CHANGED and WHAT TO DO NEXT. Don't describe what's in the images.
        
        Provide responses in BOTH Arabic and English for each section.
        
        {f'Project Context: {context}' if context else ''}
        
        Return your response in this exact JSON format:
        {{
            "changes": [
                {{
                    "category": "layout|colors|typography|spacing|content|components|effects",
                    "description_en": "Direct action item in English",
                    "description_ar": "Direct action item in Arabic",
                    "severity": "minor|moderate|major",
                    "location": "specific area/component name",
                    "action_required": "What the designer needs to do next"
                }}
            ],
            "similarity_score": 85.5,
            "summary_en": "Brief summary of main changes in English",
            "summary_ar": "Brief summary of main changes in Arabic",
            "designer_notes_en": [
                "Direct instruction for designer 1",
                "Direct instruction for designer 2"
            ],
            "designer_notes_ar": [
                "تعليمات مباشرة للمصمم 1",
                "تعليمات مباشرة للمصمم 2"
            ],
            "next_steps_en": [
                "Immediate action required",
                "Follow-up task"
            ],
            "next_steps_ar": [
                "إجراء مطلوب فوراً",
                "مهمة متابعة"
            ]
        }}
        """
        
        try:
            # Send both images to Gemini
            response = self.model.generate_content([prompt, image1, image2])
            
            # Parse JSON response
            response_text = response.text.strip()
            # Clean up response if needed
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            data = json.loads(response_text)
            
            # Convert to model objects
            changes = [
                DesignChange(
                    category=change["category"],
                    description_en=change.get("description_en", ""),
                    description_ar=change.get("description_ar", ""),
                    severity=change["severity"],
                    location=change.get("location"),
                    action_required=change.get("action_required")
                ) for change in data.get("changes", [])
            ]
            
            return AnalysisResponse(
                success=True,
                timestamp=datetime.now(),
                data=AnalysisData(
                    similarity_score=data.get("similarity_score", 0),
                    summary_en=data.get("summary_en", ""),
                    summary_ar=data.get("summary_ar", ""),
                    changes_detected=changes,
                    designer_notes_en=data.get("designer_notes_en", []),
                    designer_notes_ar=data.get("designer_notes_ar", []),
                    next_steps_en=data.get("next_steps_en", []),
                    next_steps_ar=data.get("next_steps_ar", [])
                )
            )
            
        except json.JSONDecodeError as e:
            return AnalysisResponse(
                success=False,
                timestamp=datetime.now(),
                data=AnalysisData(
                    similarity_score=0,
                    summary_en="",
                    summary_ar="",
                    changes_detected=[],
                    designer_notes_en=[],
                    designer_notes_ar=[],
                    next_steps_en=[],
                    next_steps_ar=[]
                ),
                error=f"Failed to parse AI response: {str(e)}"
            )
        except Exception as e:
            return AnalysisResponse(
                success=False,
                timestamp=datetime.now(),
                data=AnalysisData(
                    similarity_score=0,
                    summary_en="",
                    summary_ar="",
                    changes_detected=[],
                    designer_notes_en=[],
                    designer_notes_ar=[],
                    next_steps_en=[],
                    next_steps_ar=[]
                ),
                error=f"Analysis failed: {str(e)}"
            )
    
    def get_rate_limit_status(self) -> Dict:
        """Get current rate limit status"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        recent_requests = len([t for t in self.request_times if t > minute_ago])
        
        return {
            "requests_per_minute_used": recent_requests,
            "requests_per_minute_limit": config.REQUESTS_PER_MINUTE,
            "daily_requests_used": self.daily_requests,
            "daily_requests_limit": config.REQUESTS_PER_DAY,
            "can_make_request": recent_requests < config.REQUESTS_PER_MINUTE and self.daily_requests < config.REQUESTS_PER_DAY
        }