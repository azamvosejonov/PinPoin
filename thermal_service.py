import math
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ThermalCalculationService:
    """Thermal prediction using Newton's Law of Cooling"""
    
    @staticmethod
    def predict_temperature(
        initial_temp: float,
        external_temp: float,
        insulation_coefficient: float,
        time_minutes: float,
        bag_open_count: int = 0
    ) -> float:
        """
        Predict temperature after given time using Newton's Law of Cooling
        
        Formula: T(t) = T_ambient + (T_initial - T_ambient) * e^(-kt)
        
        Args:
            initial_temp: Initial food temperature (°C)
            external_temp: External ambient temperature (°C)
            insulation_coefficient: Insulation quality (0.5-1.0, higher is better)
            time_minutes: Time elapsed in minutes
            bag_open_count: Number of times bag was opened (increases cooling)
        
        Returns:
            Predicted temperature (°C)
        """
        try:
            # k is the cooling constant, depends on insulation
            k = 0.1 * insulation_coefficient
            
            # Bag opening factor: each opening reduces insulation by 10%
            effective_insulation = insulation_coefficient * (0.9 ** bag_open_count)
            k = 0.1 * effective_insulation
            
            # Newton's Law of Cooling
            temp_at_time = external_temp + (initial_temp - external_temp) * math.exp(-k * time_minutes)
            
            return round(temp_at_time, 1)
            
        except Exception as e:
            logger.error(f"Thermal calculation error: {e}")
            return initial_temp
    
    @staticmethod
    def calculate_difficulty_time(
        floors: int,
        has_elevator: bool,
        elevator_type: str = None
    ) -> int:
        """
        Calculate time to reach customer's floor
        
        Args:
            floors: Number of floors
            has_elevator: Whether building has elevator
            elevator_type: Type of elevator (CHIP_REQUIRED, CODE_REQUIRED, etc.)
        
        Returns:
            Additional time in seconds
        """
        base_time = 0
        
        if has_elevator:
            base_time = 60  # 1 minute for elevator
            
            if elevator_type == "CHIP_REQUIRED":
                base_time += 30  # Extra time for chip
            elif elevator_type == "CODE_REQUIRED":
                base_time += 15  # Extra time for code
        else:
            # Stairs: 15 seconds per floor
            base_time = floors * 15
        
        return base_time
    
    @staticmethod
    def is_thermal_critical(
        predicted_temp: float,
        min_acceptable: float,
        max_acceptable: float
    ) -> Dict[str, Any]:
        """
        Check if temperature is within acceptable range
        
        Returns:
            {'is_critical': bool, 'message': str, 'priority': str}
        """
        is_critical = predicted_temp < min_acceptable or predicted_temp > max_acceptable
        
        if is_critical:
            if predicted_temp < min_acceptable:
                message = f"Food too cold: {predicted_temp}°C (min: {min_acceptable}°C)"
                priority = "HIGH"
            else:
                message = f"Food too hot: {predicted_temp}°C (max: {max_acceptable}°C)"
                priority = "HIGH"
        else:
            message = f"Temperature acceptable: {predicted_temp}°C"
            priority = "NORMAL"
        
        return {
            'is_critical': is_critical,
            'message': message,
            'priority': priority
        }
