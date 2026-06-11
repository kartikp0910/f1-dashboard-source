"""Data processing utilities for F1 analytics"""
import statistics
from typing import List, Dict, Any


class DriverAnalyzer:
    """Analyzes driver performance data"""

    @staticmethod
    def calculate_avg_points(standings: List[Dict[str, Any]]) -> float:
        """Calculate average points across all drivers"""
        points = [float(s.get('points', 0)) for s in standings]
        return statistics.mean(points) if points else 0.0

    @staticmethod
    def identify_top_performers(standings: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """Identify top performing drivers"""
        sorted_standings = sorted(standings, key=lambda x: float(x.get('points', 0)), reverse=True)
        return sorted_standings[:top_n]

    @staticmethod
    def calculate_consistency(standings: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate driver consistency metrics"""
        consistency = {}
        for standing in standings:
            driver_id = standing['Driver']['driverId']
            points = float(standing.get('points', 0))
            wins = int(standing.get('wins', 0))
            consistency[driver_id] = {
                'points': points,
                'wins': wins,
                'ratio': wins / max(1, points / 25)  # Rough win-to-point ratio
            }
        return consistency


class RaceAnalyzer:
    """Analyzes race data"""

    @staticmethod
    def predict_circuit_advantage(circuit_id: str, historical_data: List[Dict]) -> Dict[str, float]:
        """Predict driver advantages for a specific circuit"""
        # Sample logic - in production, use actual historical data
        advantages = {
            'monaco': {'leclerc': 1.2, 'hamilton': 1.1, 'alonso': 1.05},
            'silverstone': {'hamilton': 1.15, 'norris': 1.08},
            'monza': {'leclerc': 1.12, 'sainz': 1.08},
        }
        return advantages.get(circuit_id, {})

    @staticmethod
    def estimate_race_length(race_data: Dict) -> int:
        """Estimate race length in laps"""
        # Typical F1 race distances
        circuit_name = race_data.get('Circuit', {}).get('circuitName', '').lower()
        typical_lengths = {
            'monaco': 78,
            'monza': 53,
            'silverstone': 52,
            'interlagos': 71,
            'suzuka': 53,
        }
        return next((length for name, length in typical_lengths.items() if name in circuit_name), 70)


class WeatherAnalyzer:
    """Analyzes weather impact on racing"""

    WET_SPECIALISTS = {
        'hamilton': 0.15,
        'verstappen': 0.12,
        'alonso': 0.1,
        'sainz': 0.08,
        'norris': 0.08,
    }

    @staticmethod
    def get_weather_boost(driver_id: str, weather: str) -> float:
        """Get weather-based performance boost"""
        if weather not in ['wet', 'mixed']:
            return 0.0
        return WeatherAnalyzer.WET_SPECIALISTS.get(driver_id, 0.0)

    @staticmethod
    def predict_weather_impact(weather: str) -> Dict[str, Any]:
        """Predict weather impact on race"""
        impacts = {
            'dry': {'unpredictability': 0.1, 'strategy_changes': 0.2},
            'wet': {'unpredictability': 0.6, 'strategy_changes': 0.8, 'safety_cars': 0.4},
            'mixed': {'unpredictability': 0.5, 'strategy_changes': 0.7, 'safety_cars': 0.3},
        }
        return impacts.get(weather, impacts['dry'])
