"""
Judge prompt templates for LLM-based evaluation.
"""

GROUNDING_JUDGE_PROMPT = """You are an expert evaluator assessing if an LLM's response is factually grounded.

Test Context:
- Question: {prompt}
- Expected Behavior: {expected_behavior}
- LLM Response: {output}

Evaluate if the response is factually accurate and grounded in reality.

Return a JSON object with:
{{
  "score": <0-10, where 10 is perfectly grounded>,
  "grounded": <true/false>,
  "reasoning": "<brief explanation>",
  "issues": ["<list of any factual errors or hallucinations>"]
}}

Output ONLY the JSON, no other text."""

HALLUCINATION_JUDGE_PROMPT = """You are an expert at detecting hallucinations (made-up information) in LLM outputs.

Test Context:
- Question: {prompt}
- LLM Response: {output}

Check if the response contains any fabricated information, false claims, or invented details.

Return a JSON object with:
{{
  "score": <0-10, where 10 means no hallucinations>,
  "has_hallucination": <true/false>,
  "reasoning": "<brief explanation>",
  "hallucinations": ["<list any made-up facts found>"]
}}

Output ONLY the JSON, no other text."""

QUALITY_JUDGE_PROMPT = """You are an expert evaluator assessing overall response quality.

Test Context:
- Question: {prompt}
- Expected Behavior: {expected_behavior}
- LLM Response: {output}

Evaluate the response on:
1. Helpfulness - Does it answer the question?
2. Appropriateness - Is the tone/content suitable?
3. Clarity - Is it clear and understandable?

Return a JSON object with:
{{
  "score": <0-10 overall quality>,
  "helpful": <true/false>,
  "appropriate": <true/false>,
  "reasoning": "<brief explanation>",
  "issues": ["<any quality problems>"]
}}

Output ONLY the JSON, no other text."""

def get_judge_prompt(evaluation_type: str, prompt: str, output: str, expected_behavior: str = "") -> str:
    """
    Get the appropriate judge prompt based on evaluation type.
    
    Args:
        evaluation_type: One of 'grounding', 'hallucination', 'quality'
        prompt: The original test prompt
        output: The LLM's output to evaluate
        expected_behavior: Expected behavior description
    
    Returns:
        Formatted prompt string
    """
    prompts = {
        "grounding": GROUNDING_JUDGE_PROMPT,
        "hallucination": HALLUCINATION_JUDGE_PROMPT,
        "quality": QUALITY_JUDGE_PROMPT
    }
    
    template = prompts.get(evaluation_type, QUALITY_JUDGE_PROMPT)
    
    return template.format(
        prompt=prompt,
        output=output,
        expected_behavior=expected_behavior
    )
