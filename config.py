import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", 10485760))
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "png,jpg,jpeg,webp,gif").split(",")
    PORT = int(os.getenv("PORT", 8000))
    
    # Rate limiting settings (respecting Gemini's free tier)
    REQUESTS_PER_MINUTE = 15
    REQUESTS_PER_DAY = 1500

config = Config()