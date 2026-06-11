"""ML prediction utilities"""
import random
from typing import List, Dict, Any


class PredictionModel:
    """Machine learning prediction model for F1 races"""

    def __init__(self, model_type: str = "ensemble"):
        self.model_type = model_type
        self.weights = {
            'recent_form': 0.25,
            'car_performance': 0.30,
            'circuit_history': 0.15,
            'qualifying_pace': 0.15,
            'tyre_management': 0.08,
            'weather_adaptability': 0.07,
        }

    def predict_winner(self, standings: List[Dict], circuit_id: str, 
                      weather: str = 'dry', circuit_boosts: Dict = None) -> List[Dict]:
        """Predict race winner and podium"""
        if circuit_boosts is None:
            circuit_boosts = {}

        predictions = []
        for standing in standings[:20]:
            driver = standing['Driver']
            driver_id = driver['driverId']
            
            score = self._calculate_score(
                standing, driver_id, circuit_id, weather, circuit_boosts
            )
            
            predictions.append({
                'driver_id': driver_id,
                'driver_name': f"{driver['givenName']} {driver['familyName']}",
                'score': score,
                'standing': standing
            })

        predictions.sort(key=lambda x: x['score'], reverse=True)
        return predictions

    def _calculate_score(self, standing: Dict, driver_id: str, circuit_id: str,
                        weather: str, circuit_boosts: Dict) -> float:
        """Calculate prediction score for a driver"""
        position = int(standing.get('position', 25))
        points = float(standing.get('points', 0))
        wins = int(standing.get('wins', 0))

        # Normalize scores
        car_perf = max(0, min(1, 1 - (position - 1) / 25))
        recent_form = min(1, points / 500)
        circuit_boost = circuit_boosts.get(driver_id, 0.3)
        qualifying = max(0.5, min(1, 1 - (position - 1) * 0.04))
        tyre_mgmt = 0.4 + random.random() * 0.5
        weather_adapt = 0.5 + (0.15 if weather == 'wet' and driver_id in ['hamilton', 'verstappen'] else 0)

        # Weighted score
        score = (
            self.weights['car_performance'] * car_perf +
            self.weights['recent_form'] * recent_form +
            self.weights['circuit_history'] * circuit_boost +
            self.weights['qualifying_pace'] * qualifying +
            self.weights['tyre_management'] * tyre_mgmt +
            self.weights['weather_adaptability'] * weather_adapt
        )

        return score

    def calculate_confidence(self, weather: str = 'dry') -> float:
        """Calculate model confidence level"""
        base_confidence = 0.75
        weather_adjustment = {
            'dry': 0.03,
            'mixed': -0.10,
            'wet': -0.15,
        }
        return base_confidence + weather_adjustment.get(weather, 0)
