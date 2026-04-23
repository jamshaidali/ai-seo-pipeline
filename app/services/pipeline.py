import traceback
from datetime import datetime, timezone
from app.extensions import db
from app.models.profile import BusinessProfile
from app.models.run import PipelineRun
from app.models.query import DiscoveredQuery
from app.models.recommendation import ContentRecommendation

from app.agents import QueryDiscoveryAgent, VisibilityScoringAgent, ContentRecommendationAgent
from app.utils.scoring import calculate_opportunity_score

class AI_Visibility_Pipeline:
    def __init__(self, profile_uuid: str):
        self.profile_uuid = profile_uuid
        self.profile = db.session.get(BusinessProfile, profile_uuid)
        if not self.profile:
            raise ValueError(f"Profile {profile_uuid} not found")
        
        self.run_record = PipelineRun(profile_uuid=profile_uuid)
        db.session.add(self.run_record)
        db.session.commit()
    
    def execute(self):
        try:
            self.run_record.status = 'discovering'
            db.session.commit()
            
            # Agent 1
            discovery_agent = QueryDiscoveryAgent()
            queries = discovery_agent.run(
                p_name=self.profile.name,
                p_domain=self.profile.domain,
                p_industry=self.profile.industry,
                p_desc=self.profile.description,
                p_competitors=self.profile.competitors
            )
            
            self.run_record.queries_discovered = len(queries)
            
            db_queries = []
            for qt in queries:
                q = DiscoveredQuery(
                    profile_uuid=self.profile_uuid,
                    run_uuid=self.run_record.uuid,
                    query_text=qt
                )
                db.session.add(q)
                db_queries.append(q)
                
            db.session.commit()
            
            # Agent 2
            self.run_record.status = 'scoring'
            db.session.commit()
            
            scoring_agent = VisibilityScoringAgent()
            scored_count = 0
            
            top_queries_for_recommendation = []
            
            for db_q in db_queries:
                try:
                    score_res = scoring_agent.run(db_q.query_text, self.profile.domain)
                    db_q.estimated_search_volume = score_res.estimated_search_volume
                    db_q.competitive_difficulty = score_res.competitive_difficulty
                    db_q.domain_visible = score_res.domain_visible
                    db_q.visibility_position = score_res.visibility_position
                    
                    db_q.opportunity_score = calculate_opportunity_score(
                        search_volume=db_q.estimated_search_volume,
                        difficulty=db_q.competitive_difficulty,
                        domain_visible=db_q.domain_visible,
                        query_text=db_q.query_text
                    )
                    scored_count += 1
                    
                    # Accumulate for agent 3 (High score + not visible)
                    if not db_q.domain_visible and db_q.opportunity_score >= 0.6:
                        top_queries_for_recommendation.append(db_q)
                        
                except Exception as e:
                    print(f"Failed to score query '{db_q.query_text}': {e}")
                    # Handle partial failure by continuing to next query
                    continue
                    
            self.run_record.queries_scored = scored_count
            db.session.commit()
            
            # Agent 3
            self.run_record.status = 'recommending'
            db.session.commit()
            
            rec_agent = ContentRecommendationAgent()
            
            # Sort top queries by opportunity descending, pick top 3
            top_queries_for_recommendation.sort(key=lambda x: x.opportunity_score, reverse=True)
            for target_q in top_queries_for_recommendation[:3]:
                try:
                    recs = rec_agent.run(target_q.query_text, self.profile.domain, {})
                    for rec_data in recs:
                        cr = ContentRecommendation(
                            profile_uuid=self.profile_uuid,
                            query_uuid=target_q.uuid,
                            content_type=rec_data.content_type,
                            title=rec_data.title,
                            rationale=rec_data.rationale,
                            target_keywords=rec_data.target_keywords,
                            priority=rec_data.priority
                        )
                        db.session.add(cr)
                except Exception as e:
                    print(f"Failed to generate recs for query '{target_q.query_text}': {e}")
                    continue
                    
            db.session.commit()
            
            # Finalize Run
            self.run_record.status = 'completed'
            self.run_record.completed_at = datetime.now(timezone.utc)
            db.session.commit()
            
            return self.run_record
        
        except Exception as e:
            db.session.rollback()
            self.run_record.status = 'failed'
            self.run_record.error_message = str(e)
            self.run_record.completed_at = datetime.now(timezone.utc)
            db.session.add(self.run_record)
            db.session.commit()
            traceback.print_exc()
            raise e
