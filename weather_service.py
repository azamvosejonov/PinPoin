import requests
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class WeatherService:
    """OpenWeatherMap API - Free tier available"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    API_KEY = "YOUR_OPENWEATHER_API_KEY"  # Get free key from openweathermap.org
    
    @staticmethod
    def get_current_weather(lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """
        Get current weather for location
        Returns: {'temp': float, 'humidity': int, 'description': str}
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': WeatherService.API_KEY,
                'units': 'metric'
            }
            
            response = requests.get(
                f"{WeatherService.BASE_URL}/weather",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'temp': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'description': data['weather'][0]['description']
                }
            return None
            
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            # Return default temperature if API fails
            return {'temp': 25.0, 'humidity': 50, 'description': 'clear'}
