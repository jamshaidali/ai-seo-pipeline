from flask import Blueprint, jsonify
from app.extensions import db, limiter
from app.models.query import DiscoveredQuery
from app.models.profile import BusinessProfile
from app.agents import VisibilityScoringAgent
from app.utils.scoring import calculate_opportunity_score

bp = Blueprint('queries', __name__)

@bp.route('/queries/<uuid:query_uuid>/recheck', methods=['POST'])
@limiter.limit("20 per hour")
def recheck_query(query_uuid):
    query = db.session.get(DiscoveredQuery, str(query_uuid))
    if not query:
        return jsonify({"error": "Query not found"}), 404
        
    profile = db.session.get(BusinessProfile, query.profile_uuid)
    
    try:
        agent = VisibilityScoringAgent()
        score_res = agent.run(query.query_text, profile.domain)
        
        query.estimated_search_volume = score_res.estimated_search_volume
        query.competitive_difficulty = score_res.competitive_difficulty
        query.domain_visible = score_res.domain_visible
        query.visibility_position = score_res.visibility_position
        
        query.opportunity_score = calculate_opportunity_score(
            search_volume=query.estimated_search_volume,
            difficulty=query.competitive_difficulty,
            domain_visible=query.domain_visible,
            query_text=query.query_text
        )
        
        db.session.commit()
        return jsonify(query.to_dict()), 200
        
    except Exception as e:
        return jsonify({"error": "Recheck failed: " + str(e)}), 500
