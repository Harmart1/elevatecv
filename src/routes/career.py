from flask import Blueprint, jsonify, request
import random
from datetime import datetime, timedelta

# Corrected imports for the app factory pattern
from src.routes.auth import token_required

career_bp = Blueprint('career', __name__)

@career_bp.route('/dashboard', methods=['GET'])
@token_required
def get_career_dashboard(current_user):
    """Get career dashboard overview for the logged-in user."""
    try:
        # Mock career metrics for demonstration
        dashboard_data = {
            "career_score": random.randint(80, 95),
            "key_metrics": {
                "job_market_growth": f"{random.randint(120, 160)}%",
                "market_salary": f"${random.randint(85, 120)}K",
                "skill_match": f"{random.uniform(7.5, 9.5):.1f}/10",
                "open_positions": random.randint(40, 60)
            },
            "last_updated": datetime.utcnow().isoformat()
        }

        return jsonify({"success": True, "dashboard": dashboard_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@career_bp.route('/market-trends', methods=['GET'])
@token_required
def get_market_trends(current_user):
    """Get job market trends data."""
    try:
        industry = request.args.get('industry', 'technology')
        # This endpoint can be expanded to use real data from a job market API
        trends_data = []
        base_demand = random.randint(100, 200)

        for i in range(90): # Last 90 days
            date = datetime.utcnow() - timedelta(days=89-i)
            demand = base_demand + random.randint(-20, 30) + (i * 0.5)
            trends_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "job_demand": int(demand),
            })

        return jsonify({
            "success": True,
            "industry": industry,
            "trends": trends_data,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Other career-related endpoints like salary-benchmark, skill-analysis, etc.
# would follow a similar pattern, using @token_required and accessing current_user.
