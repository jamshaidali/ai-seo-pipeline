import os
import json
import logging
import hashlib
import random
from openai import OpenAI
try:
    from anthropic import Anthropic
except Exception:
    Anthropic = None
from pydantic import BaseModel

logger = logging.getLogger('app')


class BaseAgent:
    def __init__(self):
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        self.provider = None
        self.client = None
        self.model = None

        # Prefer OpenAI if both are present; otherwise try Anthropic, with graceful fallback to mock
        if self.openai_key:
            try:
                self.client = OpenAI(api_key=self.openai_key)
                self.provider = 'openai'
                self.model = 'gpt-4o'
            except Exception as e:
                logger.warning('OpenAI client init failed: %s', e)
                self.provider = 'mock'
        elif self.anthropic_key and Anthropic is not None:
            try:
                # Anthropic client initialization can sometimes fail due to httpx/proxies incompatibilities
                self.client = Anthropic(api_key=self.anthropic_key)
                self.provider = 'anthropic'
                self.model = 'claude-3-5-sonnet-20241022'
            except Exception as e:
                logger.warning('Anthropic client init failed: %s; falling back to mock provider', e)
                self.provider = 'mock'
        else:
            self.provider = 'mock'

    def _mock_response(self, system_prompt: str, user_prompt: str, response_model: BaseModel):
        """Create deterministic mock responses seeded by the user_prompt."""
        seed = int(hashlib.sha1(user_prompt.encode('utf-8')).hexdigest()[:8], 16)
        rnd = random.Random(seed)
        name = response_model.__name__.lower()

        if 'discover' in name or 'query' in name and 'response' in name:
            # Generate 5-12 plausible queries
            n = rnd.randint(5, 12)
            queries = [f"How to choose {rnd.choice(['software','service','product'])} for {rnd.choice(['small businesses','home users','developers'])}?" for _ in range(n)]
            return response_model.model_validate({'queries': queries})

        if 'scoring' in name or 'score' in name or 'scoringresponse' in name:
            domain_visible = rnd.choice([True, False])
            visibility_position = rnd.randint(1, 10) if domain_visible else None
            data = {
                'estimated_search_volume': rnd.randint(20, 20000),
                'competitive_difficulty': rnd.randint(5, 95),
                'domain_visible': domain_visible,
                'visibility_position': visibility_position
            }
            return response_model.model_validate(data)

        if 'recommend' in name or 'recommendation' in name:
            recs = []
            for i in range(3):
                recs.append({
                    'content_type': rnd.choice(['blog_post', 'landing_page', 'faq']),
                    'title': f"{rnd.choice(['Ultimate','Complete','Beginner'])} Guide to {rnd.choice(['using','choosing','comparing'])} {rnd.choice(['X','Y','Z'])}",
                    'rationale': 'Designed to capture search intent and incorporate target keywords.',
                    'target_keywords': [f"{rnd.choice(['best','compare','review'])} {rnd.choice(['product','service'])}"] ,
                    'priority': rnd.choice(['high','medium','low'])
                })
            return response_model.model_validate({'recommendations': recs})

        # Default: return empty model
        return response_model.model_validate({})

    def invoke_structured(self, system_prompt: str, user_prompt: str, response_model: BaseModel):
        """
        Invokes the LLM API and enforces the output to match the Pydantic schema.
        Falls back to deterministic mocks if an LLM provider is not available.
        """
        try:
            if self.provider == 'openai':
                completion = self.client.beta.chat.completions.parse(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format=response_model
                )
                return completion.choices[0].message.parsed
            elif self.provider == 'anthropic':
                # For Anthropic, use tool calling to enforce schema
                from pydantic import TypeAdapter
                schema = response_model.model_json_schema()

                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ],
                    tools=[{
                        "name": "structured_response",
                        "description": "Provide a structured response matching the schema",
                        "input_schema": schema
                    }],
                    tool_choice={"type": "tool", "name": "structured_response"}
                )

                tool_call = message.content[0]
                if tool_call.type == 'tool_use':
                    return response_model.model_validate(tool_call.input)
                else:
                    raise RuntimeError("Failed to get structured response from Claude")

            else:
                # Mock provider
                logger.info('Using mock provider for response: %s', response_model.__name__)
                return self._mock_response(system_prompt, user_prompt, response_model)

        except Exception as e:
            raise RuntimeError(f"Agent execution failed: {str(e)}")
