import pytest
from unittest.mock import patch, MagicMock
from app.agents.discovery import QueryDiscoveryAgent, DiscoveredQueriesResponse
from app.agents.scoring import VisibilityScoringAgent, ScoringResponse
from app.agents.recommendation import ContentRecommendationAgent, RecommendationsResponse, ContentRecommendationModel

def test_query_discovery_agent():
    agent = QueryDiscoveryAgent()
    agent.client = MagicMock()
    
    mock_response = DiscoveredQueriesResponse(queries=[\"Best AI tools\", \"Surfer vs Frase\"])
    agent.invoke_structured = MagicMock(return_value=mock_response)
    
    result = agent.run(\"Test\", \"test.com\", \"SEO\", \"Desc\", [\"comp1.com\"])
    assert len(result) == 2
    assert \"Best AI tools\" in result
    agent.invoke_structured.assert_called_once()

def test_visibility_scoring_agent():
    agent = VisibilityScoringAgent()
    mock_response = ScoringResponse(
        estimated_search_volume=1500,
        competitive_difficulty=65,
        domain_visible=False,
        visibility_position=None
    )
    agent.invoke_structured = MagicMock(return_value=mock_response)
    
    res = agent.run(\"Best AI tools\", \"test.com\")
    assert res.estimated_search_volume == 1500
    assert not res.domain_visible

def test_content_recommendation_agent():
    agent = ContentRecommendationAgent()
    mock_rec = ContentRecommendationModel(
        content_type=\"blog_post\",
        title=\"Top Tools 2025\",
        rationale=\"Because it is good\",
        target_keywords=[\"seo\", \"tools\"],
        priority=\"high\"
    )
    mock_response = RecommendationsResponse(recommendations=[mock_rec])
    agent.invoke_structured = MagicMock(return_value=mock_response)
    
    res = agent.run(\"Best AI tools\", \"test.com\", {})
    assert len(res) == 1
    assert res[0].content_type == \"blog_post\"
