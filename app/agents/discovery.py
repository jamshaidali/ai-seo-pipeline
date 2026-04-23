from typing import List
from pydantic import BaseModel, Field
from app.agents.base import BaseAgent

class DiscoveredQueriesResponse(BaseModel):
    queries: List[str] = Field(description="List of commercially relevant, natural-language search queries discovered.")

class QueryDiscoveryAgent(BaseAgent):
    def run(self, p_name: str, p_domain: str, p_industry: str, p_desc: str, p_competitors: List[str]) -> List[str]:
        system_prompt = """
        You are an expert SEO Strategist specializing in uncovering high-value search queries.
        Your task is to generate a set of 10 to 20 realistic questions that users are likely to ask AI 
        assistants or search engines when looking for products or services in the provided business space.
        
        Focus heavily on:
        - Commercial intent (e.g. "Best [x] for [y]", "[Brand] vs [Competitor]").
        - Questions highlighting alternative solutions.
        - Long-tail problem-solving inquiries relevant to the domain.
        
        ONLY output valid JSON matching the schema.
        """
        
        user_prompt = f"""
        Business Name: {p_name}
        Domain: {p_domain}
        Industry: {p_industry}
        Description: {p_desc}
        Competitors: {', '.join(p_competitors)}
        
        Generate 10-20 search queries users would search for to find this business or its competitors.
        """
        
        result = self.invoke_structured(system_prompt, user_prompt, DiscoveredQueriesResponse)
        # Sliced to max 20 to ensure constraints
        return result.queries[:20]
