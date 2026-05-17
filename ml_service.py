import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class TrajectoryClusteringService:
    """ML-based trajectory analysis for podyezd detection"""
    
    @staticmethod
    def analyze_trajectory(
        vehicle_stops: List[Tuple[float, float]],
        pedestrian_points: List[Tuple[float, float]],
        use_cold_start: bool = False
    ) -> Optional[dict]:
        """
        Analyze trajectory to identify podyezd entrance
        
        Args:
            vehicle_stops: List of (lat, lon) where vehicle stopped
            pedestrian_points: List of (lat, lon) where pedestrian walked
            use_cold_start: If True, use fallback logic for new buildings
        
        Returns:
            {'entrance_lat': float, 'entrance_lon': float, 'confidence': float}
        """
        try:
            # Cold start logic for new buildings
            if use_cold_start or len(vehicle_stops) < 2 or len(pedestrian_points) < 2:
                # Fallback: Use last pedestrian point as entrance
                if pedestrian_points:
                    last_point = pedestrian_points[-1]
                    return {
                        'entrance_lat': last_point[0],
                        'entrance_lon': last_point[1],
                        'confidence': 0.5,  # Low confidence for cold start
                        'method': 'cold_start'
                    }
                return None
            
            # Combine all points
            all_points = np.array(vehicle_stops + pedestrian_points)
            
            # Normalize coordinates
            scaler = StandardScaler()
            scaled_points = scaler.fit_transform(all_points)
            
            # Apply DBSCAN clustering
            clustering = DBSCAN(eps=0.0001, min_samples=3)
            labels = clustering.fit_predict(scaled_points)
            
            # Find the cluster with most pedestrian points
            pedestrian_array = np.array(pedestrian_points)
            pedestrian_scaled = scaler.transform(pedestrian_array)
            
            if len(labels) > 0:
                unique_labels = set(labels)
                best_cluster = None
                max_pedestrian_count = 0
                
                for label in unique_labels:
                    if label == -1:
                        continue
                    
                    cluster_mask = labels == label
                    pedestrian_in_cluster = np.sum(cluster_mask[len(vehicle_stops):])
                    
                    if pedestrian_in_cluster > max_pedestrian_count:
                        max_pedestrian_count = pedestrian_in_cluster
                        best_cluster = label
                
                if best_cluster is not None:
                    cluster_mask = labels == best_cluster
                    cluster_points = all_points[cluster_mask]
                    
                    # Calculate centroid
                    centroid = np.mean(cluster_points, axis=0)
                    
                    # Calculate confidence based on cluster density
                    confidence = min(1.0, max_pedestrian_count / 3.0)
                    
                    return {
                        'entrance_lat': centroid[0],
                        'entrance_lon': centroid[1],
                        'confidence': confidence,
                        'method': 'ml_clustering'
                    }
            
            # Fallback to cold start if clustering fails
            if pedestrian_points:
                last_point = pedestrian_points[-1]
                return {
                    'entrance_lat': last_point[0],
                    'entrance_lon': last_point[1],
                    'confidence': 0.5,
                    'method': 'cold_start'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Trajectory clustering error: {e}")
            return None
    
    @staticmethod
    def confirm_entrance(
        new_point: Tuple[float, float],
        existing_entrances: List[Tuple[float, float]],
        threshold_meters: float = 10.0
    ) -> bool:
        """
        Check if new point matches existing entrance
        """
        try:
            for entrance in existing_entrances:
                # Simple distance calculation (approximate)
                lat_diff = abs(new_point[0] - entrance[0]) * 111000  # meters per degree latitude
                lon_diff = abs(new_point[1] - entrance[1]) * 111000  # approximate
                distance = (lat_diff ** 2 + lon_diff ** 2) ** 0.5
                
                if distance < threshold_meters:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Entrance confirmation error: {e}")
            return False
