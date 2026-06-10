#!/usr/bin/env python3
# PATCHED
# Date: 2025-07-21
# Task: Updated OpenAI prompt to meet API requirements for JSON output.
# Source: uploaded:gpt_feature_ideator.py

import os
import json
import openai
import logging
from .feature_registry import FeatureRegistry
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('GPTIdeator')

class GPTFeatureIdeator:
    def __init__(self, registry: FeatureRegistry, model="gpt-4-turbo"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        openai.api_key = api_key

        self.registry = registry
        self.model = model
        logger.info("GPT feature ideator initialized")

    def _generate_prompt(self, category: str, existing_names: list):
        return f"""
You are a senior quantitative analyst specializing in cryptocurrency trading. 
Generate 3 novel technical features in the '{category}' category that haven't been documented before.

**Constraints:**
- Must be computationally efficient (O(n) complexity)
- Must use only OHLCV data
- Must be implemented in pandas
- Must not resemble these existing features: {', '.join(existing_names[:5])}...

**Response Instructions:**
You must respond in a valid JSON format that follows the schema below.

**Output Format:**
{{
  "features": [
    {{
      "name": "snake_case_name",
      "description": "1-2 sentence explanation",
      "code_logic": "df['feature_name'] = ..."
    }}
  ]
}}
"""

    def generate_and_log_features(self, category: str):
        logger.info(f"Generating ideas for category: '{category}'")
        self.registry.cursor.execute("SELECT name FROM features")
        existing = [row[0] for row in self.registry.cursor.fetchall()]

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": self._generate_prompt(category, existing)}],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=1000
            )
            ideas = json.loads(response.choices[0].message.content)

            for idea in ideas.get('features', []):
                self.registry.add_feature_idea(
                    name=idea['name'], 
                    description=idea['description'],
                    category=category, 
                    code_logic=idea['code_logic']
                )
            return True
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            return False

if __name__ == '__main__':
    db_connection_params = {
        "dbname": "cta_db", "user": "postgre", "password": "a",
        "host": "localhost", "port": "5432"
    }
    registry = None
    try:
        registry = FeatureRegistry(db_params=db_connection_params)
        ideator = GPTFeatureIdeator(registry)
        ideator.generate_and_log_features('volatility')
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if registry:
            registry.close()