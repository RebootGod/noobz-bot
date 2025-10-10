"""
Gemini AI Service untuk generate content.
Handle API calls ke Google Gemini AI.
"""

import logging
from typing import Optional, Dict, Any
import google.generativeai as genai

from config.settings import get_settings

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Service untuk interact dengan Gemini AI.
    """
    
    def __init__(self):
        """Initialize Gemini service."""
        self.settings = get_settings()
        self._configure_api()
        self.model = None
        self._is_initialized = False
    
    def _configure_api(self):
        """Configure Gemini API dengan API key."""
        try:
            genai.configure(api_key=self.settings.gemini_api_key)
            logger.info("Gemini API configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            raise
    
    def initialize(self, model_name: str = 'gemini-2.0-flash-exp'):
        """
        Initialize Gemini model.
        
        Available models:
        - gemini-2.0-flash-exp (Latest, fastest, recommended)
        - gemini-1.5-flash (Fast, good for most tasks)
        - gemini-1.5-pro (More capable, slower)
        - gemini-pro (Legacy, stable)
        
        Args:
            model_name: Nama model yang akan digunakan
        """
        try:
            self.model = genai.GenerativeModel(model_name)
            self._is_initialized = True
            logger.info(f"Gemini model '{model_name}' initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise
    
    async def generate_announcement(
        self, 
        movie_info: Dict[str, Any], 
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        Generate announcement text untuk movie.
        
        Args:
            movie_info: Dictionary berisi info movie dari TMDB
            custom_prompt: Custom prompt dari user (optional)
            
        Returns:
            Generated announcement text
            
        Raises:
            Exception: Jika gagal generate
        """
        if not self._is_initialized:
            self.initialize()
        
        try:
            # Build prompt
            prompt = self._build_announcement_prompt(movie_info, custom_prompt)
            
            # Generate content
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise Exception("Empty response from Gemini")
            
            announcement = response.text.strip()
            
            # Truncate to max 400 characters if needed
            MAX_LENGTH = 400
            if len(announcement) > MAX_LENGTH:
                announcement = announcement[:MAX_LENGTH].rsplit(' ', 1)[0] + '...'
                logger.info(f"Announcement truncated to {MAX_LENGTH} characters")
            
            logger.info("Successfully generated announcement")
            return announcement
            
        except Exception as e:
            logger.error(f"Failed to generate announcement: {e}")
            raise
    
    def _build_announcement_prompt(
        self, 
        movie_info: Dict[str, Any], 
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        Build prompt untuk Gemini AI.
        
        Args:
            movie_info: Dictionary berisi info movie
            custom_prompt: Custom prompt dari user
            
        Returns:
            Formatted prompt string
        """
        # Extract movie info
        title = movie_info.get('title') or movie_info.get('name', 'Unknown')
        year = movie_info.get('release_date', '')[:4] if movie_info.get('release_date') else ''
        overview = movie_info.get('overview', '')
        genres = ', '.join([g['name'] for g in movie_info.get('genres', [])])
        rating = movie_info.get('vote_average', 0)
        
        # Build base prompt
        base_prompt = f"""
Buatkan announcement yang menarik dan engaging untuk film/series berikut:

Judul: {title} ({year})
Genre: {genres}
Rating: {rating}/10
Sinopsis: {overview}

Website: {self.settings.website_url}
"""
        
        # Add custom instructions jika ada
        if custom_prompt:
            base_prompt += f"\n\nInstruksi tambahan: {custom_prompt}"
        
        base_prompt += """

Requirements untuk announcement:
- Gunakan bahasa Indonesia yang casual dan friendly
- Buat catchy dan engaging untuk audience
- Include emoji yang relevan untuk mood film
- Mention bahwa film available di noobz.space
- PENTING: Maksimal 400 karakter (singkat tapi informatif!)
- Fokus pada hook yang bikin penasaran
- Ajak audience untuk nonton

Format output: langsung announcement text saja, tanpa judul atau label tambahan.
"""
        
        return base_prompt
    
    async def generate_custom_content(self, prompt: str) -> str:
        """
        Generate custom content dengan prompt bebas.
        
        Args:
            prompt: Custom prompt
            
        Returns:
            Generated content
            
        Raises:
            Exception: Jika gagal generate
        """
        if not self._is_initialized:
            self.initialize()
        
        try:
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise Exception("Empty response from Gemini")
            
            content = response.text.strip()
            logger.info("Successfully generated custom content")
            return content
            
        except Exception as e:
            logger.error(f"Failed to generate custom content: {e}")
            raise
    
    def is_ready(self) -> bool:
        """
        Check apakah service ready.
        
        Returns:
            True jika service initialized
        """
        return self._is_initialized


# Global instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """
    Get global GeminiService instance.
    
    Returns:
        GeminiService instance
    """
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
