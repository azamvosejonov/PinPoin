import requests
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GeocodingService:
    """OpenStreetMap Nominatim API - Completely Free"""
    
    BASE_URL = "https://nominatim.openstreetmap.org"
    USER_AGENT = "PinPointDelivery/1.0"
    
    @staticmethod
    def geocode(address: str) -> Optional[Dict[str, Any]]:
        """
        Convert address to coordinates
        Returns: {'lat': float, 'lon': float, 'display_name': str}
        """
        try:
            params = {
                'q': address,
                'format': 'json',
                'limit': 1
            }
            headers = {
                'User-Agent': GeocodingService.USER_AGENT
            }
            
            response = requests.get(
                f"{GeocodingService.BASE_URL}/search",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200 and response.json():
                data = response.json()[0]
                return {
                    'lat': float(data['lat']),
                    'lon': float(data['lon']),
                    'display_name': data['display_name']
                }
            return None
            
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None
    
    @staticmethod
    def reverse_geocode(lat: float, lon: float) -> Optional[str]:
        """
        Convert coordinates to address
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json'
            }
            headers = {
                'User-Agent': GeocodingService.USER_AGENT
            }
            
            response = requests.get(
                f"{GeocodingService.BASE_URL}/reverse",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('display_name')
            return None
            
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
            return None
