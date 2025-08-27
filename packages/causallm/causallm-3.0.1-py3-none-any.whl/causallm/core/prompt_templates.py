"""
Prompt templates for CausalLLM
Contains standardized prompts for causal reasoning tasks
"""
from typing import Dict, List, Optional


def get_causal_discovery_prompt(
    variables: Dict[str, str],
    domain_context: str = "",
    background_knowledge: Optional[List[str]] = None
) -> str:
    """Generate prompt for causal discovery."""
    prompt_parts = [
        "You are an expert in causal inference. Analyze the following variables and identify causal relationships.",
        "",
        "VARIABLES:"
    ]
    
    for var, desc in variables.items():
        prompt_parts.append(f"- {var}: {desc}")
    
    if domain_context:
        prompt_parts.extend(["", f"DOMAIN: {domain_context}"])
    
    if background_knowledge:
        prompt_parts.extend(["", "BACKGROUND KNOWLEDGE:"])
        for knowledge in background_knowledge:
            prompt_parts.append(f"- {knowledge}")
    
    prompt_parts.extend([
        "",
        "Identify causal relationships (X → Y) and provide reasoning for each."
    ])
    
    return "\n".join(prompt_parts)


def get_intervention_prompt(
    context: str,
    intervention: Dict[str, str],
    question: Optional[str] = None
) -> str:
    """Generate prompt for intervention analysis."""
    intervention_desc = ", ".join([f"{k} := {v}" for k, v in intervention.items()])
    
    prompt = f"""
Analyze the causal impact of the following intervention:

CONTEXT: {context}

INTERVENTION: do({intervention_desc})

{question or "What would be the expected outcomes of this intervention?"}
"""
    
    return prompt.strip()


def get_counterfactual_prompt(
    factual_scenario: str,
    counterfactual_intervention: str,
    instruction: Optional[str] = None
) -> str:
    """Generate prompt for counterfactual analysis."""
    prompt = f"""
Perform counterfactual reasoning on the following scenario:

FACTUAL SCENARIO: {factual_scenario}

COUNTERFACTUAL: {counterfactual_intervention}

{instruction or "Compare the outcomes between the factual and counterfactual scenarios."}
"""
    
    return prompt.strip()