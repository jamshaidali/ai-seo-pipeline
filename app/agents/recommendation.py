from typing import List
from pydantic import BaseModel, Field
from app.agents.base import BaseAgent

class ContentRecommendationModel(BaseModel):
    content_type: str = Field(description="Type of content (e.g., blog_post, landing_page, faq).")
    title: str = Field(description="Suggested compelling title for the content.")
    rationale: str = Field(description="Explanation of why this content addresses the query gap.")
    target_keywords: List[str] = Field(description="3-5 target keywords to include.")
    priority: str = Field(description="Priority level: high, medium, or low.")

class RecommendationsResponse(BaseModel):
    recommendations: List[ContentRecommendationModel] = Field(description="List of 3-5 specific, actionable content recommendations.")

class ContentRecommendationAgent(BaseAgent):
    def run(self, query: str, target_domain: str, intent_info: dict) -> List[ContentRecommendationModel]:
        system_prompt = """
        You are an expert Content Strategy AI.
        Your task is to review a high-value search query where the target domain is currently NOT visible 
        in AI search answers. You must generate 3 to 5 actionable content recommendations designed to capture 
        visibility for this query.
        
        Provide detailed, practical suggestions. Ensure priority makes sense given the gap.
        
        ALWAYS return valid JSON matching the schema.
        """
        
        user_prompt = f"""
        Target Domain: {target_domain}
        Query: "{query}"
        Context: The domain is currently losing out on visibility for this query.
        Generate 3-5 strategic content recommendations to close this gap.
        """
        
        res = self.invoke_structured(system_prompt, user_prompt, RecommendationsResponse)
        return res.recommendations[:5]
