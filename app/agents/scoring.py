from typing import Optional
from pydantic import BaseModel, Field
from app.agents.base import BaseAgent

class ScoringResponse(BaseModel):
    estimated_search_volume: int = Field(description="Estimated monthly search volume (mocking an SEO tool value).")
    competitive_difficulty: int = Field(description="Score from 0 to 100 on how difficult this query is to rank for.")
    domain_visible: bool = Field(description="True if the target domain is likely to be mentioned in top AI answers.")
    visibility_position: Optional[int] = Field(description="Estimated position of the domain mention. Null if domain_visible is false.")

class VisibilityScoringAgent(BaseAgent):
    def run(self, query: str, target_domain: str) -> ScoringResponse:
        system_prompt = """
        You are an advanced SEO Data Mocking API. 
        Your task is to analyze a given search query and a target domain, and return estimated (mocked) metrics 
        that a tool like DataForSEO or Ahrefs would return.
        
        Rules:
        - estimated_search_volume: Plausible monthly volume (e.g., 50 for obscure, 10000+ for broad).
        - competitive_difficulty: 0-100 scale (0 = easy, 100 = hard).
        - domain_visible: Guess if the target domain would naturally appear in an AI answer today for this query.
        - visibility_position: Integer 1-10 if visible, null otherwise.
        
        ALWAYS return valid JSON matching the schema.
        """
        
        user_prompt = f"""
        Query to analyze: "{query}"
        Target Domain: {target_domain}
        """
        
        return self.invoke_structured(system_prompt, user_prompt, ScoringResponse)
