"""Statistics and reporting utilities"""
from typing import List, Dict, Any
import statistics


class StatsCalculator:
    """Calculate F1 statistics"""

    @staticmethod
    def calculate_win_probability(predictions: List[Dict]) -> List[Dict]:
        """Convert scores to probabilities"""
        total_score = sum(p['score'] for p in predictions)
        
        if total_score == 0:
            return predictions

        for pred in predictions:
            pred['win_probability'] = pred['score'] / total_score
            pred['podium_probability'] = min(0.99, pred['win_probability'] * 2.5)

        return predictions

    @staticmethod
    def calculate_head_to_head(driver1: Dict, driver2: Dict) -> Dict[str, Any]:
        """Calculate head-to-head statistics"""
        return {
            'driver1_name': driver1['Driver']['givenName'],
            'driver2_name': driver2['Driver']['givenName'],
            'driver1_points': float(driver1.get('points', 0)),
            'driver2_points': float(driver2.get('points', 0)),
            'driver1_wins': int(driver1.get('wins', 0)),
            'driver2_wins': int(driver2.get('wins', 0)),
            'point_difference': float(driver1.get('points', 0)) - float(driver2.get('points', 0)),
        }

    @staticmethod
    def calculate_trend(historical_data: List[Dict]) -> Dict[str, float]:
        """Calculate performance trend"""
        if len(historical_data) < 2:
            return {'trend': 0.0}

        recent_scores = [d.get('score', 0) for d in historical_data[-5:]]
        older_scores = [d.get('score', 0) for d in historical_data[:-5]]

        recent_avg = statistics.mean(recent_scores) if recent_scores else 0
        older_avg = statistics.mean(older_scores) if older_scores else 0

        return {
            'trend': recent_avg - older_avg,
            'recent_average': recent_avg,
            'older_average': older_avg,
            'improving': recent_avg > older_avg
        }

    @staticmethod
    def generate_insights(predictions: List[Dict], weather: str) -> List[str]:
        """Generate text insights from predictions"""
        insights = []

        if not predictions:
            return insights

        leader = predictions[0]
        insights.append(
            f"{leader['driver_name']} is the favorite with "
            f"{leader.get('win_probability', 0) * 100:.0f}% win probability"
        )

        if weather == 'wet':
            insights.append("Wet conditions will benefit drivers strong in the rain")
        elif weather == 'mixed':
            insights.append("Mixed conditions create unpredictability - strategy will be key")

        if len(predictions) > 1:
            gap = (predictions[0].get('win_probability', 0) - 
                   predictions[1].get('win_probability', 0))
            if gap < 0.05:
                insights.append(f"Very close battle expected between top contenders")

        return insights
