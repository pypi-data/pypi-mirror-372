from typing import Dict, Optional
from ..utils.logging import get_logger, get_structured_logger

class DoOperatorSimulator:
    def __init__(self, base_context: str, variables: Dict[str, str]):
        self.logger = get_logger("causalllm.do_operator")
        self.struct_logger = get_structured_logger("do_operator")
        
        self.logger.info("Initializing DoOperatorSimulator")
        self.logger.debug(f"Context length: {len(base_context)}, Variables: {list(variables.keys())}")
        
        self.base_context = base_context
        self.variables = variables.copy()
        
        self.struct_logger.log_interaction(
            "simulator_initialization",
            {
                "context_length": len(base_context),
                "variables_count": len(variables),
                "variable_names": list(variables.keys())
            }
        )
        
        self.logger.info("DoOperatorSimulator initialized successfully")

    def intervene(self, interventions: Dict[str, str]) -> str:
        self.logger.info(f"Performing intervention: {interventions}")
        
        try:
            modified_context = self.base_context
            replacements = {}

            for var, new_val in interventions.items():
                if var not in self.variables:
                    error_msg = f"Variable '{var}' not in base context."
                    self.logger.error(error_msg)
                    raise ValueError(error_msg)
                
                original_val = self.variables[var]
                self.logger.debug(f"Replacing '{original_val}' with '{new_val}' for variable '{var}'")
                
                modified_context = modified_context.replace(original_val, new_val)
                replacements[var] = {"original": original_val, "new": new_val}
                self.variables[var] = new_val

            self.struct_logger.log_interaction(
                "intervention",
                {
                    "interventions": interventions,
                    "replacements": replacements,
                    "original_context_length": len(self.base_context),
                    "modified_context_length": len(modified_context)
                }
            )
            
            self.logger.info(f"Intervention completed successfully, modified {len(interventions)} variables")
            return modified_context
            
        except Exception as e:
            self.logger.error(f"Error during intervention: {e}")
            self.struct_logger.log_error(e, {"interventions": interventions})
            raise

    def generate_do_prompt(
        self,
        interventions: Dict[str, str],
        question: Optional[str] = None
    ) -> str:
        self.logger.info(f"Generating do-calculus prompt for interventions: {interventions}")
        self.logger.debug(f"Question: {question}")
        
        try:
            modified_context = self.intervene(interventions)
            intervention_desc = ", ".join([f"{k} := {v}" for k, v in interventions.items()])
            
            prompt = f"""
You are a causal inference model.

Base scenario:
{self.base_context}

Intervention applied:
do({intervention_desc})

Resulting scenario:
{modified_context}

{question if question else "What is the expected impact of this intervention?"}
"""
            result = prompt.strip()
            
            self.struct_logger.log_interaction(
                "generate_do_prompt",
                {
                    "interventions": interventions,
                    "question": question,
                    "intervention_desc": intervention_desc,
                    "prompt_length": len(result),
                    "base_context_length": len(self.base_context),
                    "modified_context_length": len(modified_context)
                }
            )
            
            self.logger.info(f"Do-calculus prompt generated successfully, length: {len(result)}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating do-calculus prompt: {e}")
            self.struct_logger.log_error(e, {"interventions": interventions, "question": question})
            raise
