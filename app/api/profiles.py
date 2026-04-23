from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from app.extensions import db, limiter
from app.models.profile import BusinessProfile
from app.models.query import DiscoveredQuery
from app.models.run import PipelineRun
from app.models.recommendation import ContentRecommendation
from app.schemas.profile import ProfileCreateRequest, ProfileResponse
from app.schemas.query import QueryListResponse, QueryResponse
from app.schemas.recommendation import RecommendationListResponse, RecommendationResponse
from app.services.pipeline import AI_Visibility_Pipeline

bp = Blueprint('profiles', __name__)

@bp.route('/profiles', methods=['POST'])
@limiter.limit("10 per minute")
def create_profile():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload provided"}), 400
        
        validated = ProfileCreateRequest.model_validate(data)
        
        profile = BusinessProfile(
            name=validated.name,
            domain=validated.domain,
            industry=validated.industry,
            description=validated.description,
            competitors=validated.competitors
        )
        
        db.session.add(profile)
        db.session.commit()
        
        response = ProfileResponse.model_validate(profile.to_dict())
        return response.model_dump_json(), 201

    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/profiles/<uuid:profile_uuid>', methods=['GET'])
@limiter.limit("100 per hour")
def get_profile(profile_uuid):
    profile = db.session.get(BusinessProfile, str(profile_uuid))
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
        
    runs = PipelineRun.query.filter_by(profile_uuid=str(profile_uuid)).all()
    queries = DiscoveredQuery.query.filter_by(profile_uuid=str(profile_uuid)).all()
    
    total_queries = len(queries)
    avg_score = sum([q.opportunity_score for q in queries if q.opportunity_score]) / total_queries if total_queries > 0 else 0
    
    resp = profile.to_dict()
    resp['summary_stats'] = {
        "total_queries_discovered": total_queries,
        "avg_opportunity_score": round(avg_score, 2),
        "total_runs": len(runs)
    }
    
    return jsonify(resp), 200

@bp.route('/profiles/<uuid:profile_uuid>/run', methods=['POST'])
@limiter.limit("5 per hour")
def trigger_pipeline(profile_uuid):
    try:
        pipeline = AI_Visibility_Pipeline(str(profile_uuid))
        run_record = pipeline.execute()
        
        # After execution
        # Get top queries
        top_queries = DiscoveredQuery.query.filter_by(run_uuid=run_record.uuid).order_by(DiscoveredQuery.opportunity_score.desc()).limit(3).all()
        
        # Get recommendations
        recs = []
        for q in top_queries:
            q_recs = ContentRecommendation.query.filter_by(query_uuid=q.uuid).all()
            recs.extend([r.to_dict() for r in q_recs])
        
        return jsonify({
            "pipeline_run_uuid": run_record.uuid,
            "status": run_record.status,
            "queries_discovered": run_record.queries_discovered,
            "queries_scored": run_record.queries_scored,
            "top_3_opportunity_queries": [q.to_dict() for q in top_queries],
            "content_recommendations": recs
        }), 200
        
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": "Pipeline failed: " + str(e)}), 500

@bp.route('/profiles/<uuid:profile_uuid>/queries', methods=['GET'])
@limiter.limit("100 per hour")
def get_queries(profile_uuid):
    # Filters: min_score, status, page, per_page
    min_score = request.args.get('min_score', type=float)
    status_filter = request.args.get('status', type=str)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query_obj = DiscoveredQuery.query.filter_by(profile_uuid=str(profile_uuid))
    
    if min_score is not None:
        query_obj = query_obj.filter(DiscoveredQuery.opportunity_score >= min_score)
        
    if status_filter:
        if status_filter == 'visible':
            query_obj = query_obj.filter(DiscoveredQuery.domain_visible == True)
        elif status_filter == 'not_visible':
            query_obj = query_obj.filter(DiscoveredQuery.domain_visible == False)
            
    query_obj = query_obj.order_by(DiscoveredQuery.opportunity_score.desc())
    
    pagination = query_obj.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "queries": [q.to_dict() for q in pagination.items]
    }), 200

@bp.route('/profiles/<uuid:profile_uuid>/recommendations', methods=['GET'])
@limiter.limit("100 per hour")
def get_recommendations(profile_uuid):
    recs = ContentRecommendation.query.filter_by(profile_uuid=str(profile_uuid)).order_by(ContentRecommendation.created_at.desc()).all()
    return jsonify({
        "count": len(recs),
        "recommendations": [r.to_dict() for r in recs]
    }), 200
