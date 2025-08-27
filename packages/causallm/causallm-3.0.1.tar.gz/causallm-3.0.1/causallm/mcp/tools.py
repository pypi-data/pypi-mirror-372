"""MCP tool definitions for CausalLLM functionality."""

import asyncio
from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass
from causalllm.logging import get_logger
from causalllm.core import CausalLLMCore
from causalllm.llm_client import get_llm_client, BaseLLMClient
from causalllm.counterfactual_engine import CounterfactualEngine
from causalllm.scm_explainer import SCMExplainer
from causalllm.dag_parser import DAGParser
from causalllm.do_operator import DoOperatorSimulator
from causalllm.prompt_templates import PromptTemplates

logger = get_logger("causalllm.mcp.tools")

@dataclass
class MCPTool:
    """MCP tool definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]

class CausalTools:
    """Collection of MCP tools for causal reasoning."""
    
    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        """Initialize causal tools with optional LLM client."""
        logger.info("Initializing CausalLLM MCP tools")
        
        try:
            self.llm_client = llm_client or get_llm_client("grok")  # Default to mock client
            self.counterfactual_engine = CounterfactualEngine(self.llm_client)
            self.scm_explainer = SCMExplainer(self.llm_client)
            
            # Initialize tools
            self.tools: Dict[str, MCPTool] = self._create_tools()
            
            logger.info(f"Initialized {len(self.tools)} MCP tools")
            
        except Exception as e:
            logger.error(f"Failed to initialize causal tools: {e}")
            raise RuntimeError(f"Tool initialization failed: {e}")
    
    def _create_tools(self) -> Dict[str, MCPTool]:
        """Create the collection of MCP tools."""
        return {
            "simulate_counterfactual": MCPTool(
                name="simulate_counterfactual",
                description="Simulate counterfactual scenarios by comparing factual and hypothetical situations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "context": {
                            "type": "string",
                            "description": "The background context or setting"
                        },
                        "factual": {
                            "type": "string", 
                            "description": "The factual scenario that actually happened"
                        },
                        "intervention": {
                            "type": "string",
                            "description": "The hypothetical intervention or change to consider"
                        },
                        "instruction": {
                            "type": "string",
                            "description": "Optional additional instruction for the analysis"
                        },
                        "temperature": {
                            "type": "number",
                            "description": "Temperature for LLM generation (0.0-2.0)",
                            "default": 0.7
                        },
                        "chain_of_thought": {
                            "type": "boolean",
                            "description": "Whether to use chain-of-thought reasoning",
                            "default": False
                        }
                    },
                    "required": ["context", "factual", "intervention"]
                },
                handler=self._handle_simulate_counterfactual
            ),
            
            "generate_do_prompt": MCPTool(
                name="generate_do_prompt",
                description="Generate do-calculus intervention prompts for causal analysis",
                input_schema={
                    "type": "object",
                    "properties": {
                        "context": {
                            "type": "string",
                            "description": "The base context describing the system"
                        },
                        "variables": {
                            "type": "object",
                            "description": "Dictionary mapping variable names to descriptions"
                        },
                        "intervention": {
                            "type": "object", 
                            "description": "Dictionary of variable interventions {var: new_value}"
                        },
                        "question": {
                            "type": "string",
                            "description": "Optional question to include in the analysis"
                        }
                    },
                    "required": ["context", "variables", "intervention"]
                },
                handler=self._handle_generate_do_prompt
            ),
            
            "extract_causal_edges": MCPTool(
                name="extract_causal_edges",
                description="Extract causal relationships from text descriptions",
                input_schema={
                    "type": "object",
                    "properties": {
                        "scenario_description": {
                            "type": "string",
                            "description": "Natural language description of a scenario with causal relationships"
                        },
                        "model": {
                            "type": "string",
                            "description": "LLM model to use for extraction",
                            "default": "gpt-4"
                        },
                        "temperature": {
                            "type": "number",
                            "description": "Temperature for LLM generation",
                            "default": 0.3
                        }
                    },
                    "required": ["scenario_description"]
                },
                handler=self._handle_extract_causal_edges
            ),
            
            "generate_reasoning_prompt": MCPTool(
                name="generate_reasoning_prompt", 
                description="Generate reasoning prompts from causal DAG structures",
                input_schema={
                    "type": "object",
                    "properties": {
                        "dag_edges": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 2,
                                "maxItems": 2
                            },
                            "description": "List of directed edges as [source, target] pairs"
                        },
                        "task": {
                            "type": "string",
                            "description": "The reasoning task or question",
                            "default": ""
                        }
                    },
                    "required": ["dag_edges"]
                },
                handler=self._handle_generate_reasoning_prompt
            ),
            
            "analyze_treatment_effect": MCPTool(
                name="analyze_treatment_effect",
                description="Analyze treatment effects using causal inference templates",
                input_schema={
                    "type": "object",
                    "properties": {
                        "context": {
                            "type": "string",
                            "description": "The experimental or observational context"
                        },
                        "treatment": {
                            "type": "string",
                            "description": "Description of the treatment variable"
                        },
                        "outcome": {
                            "type": "string", 
                            "description": "Description of the outcome variable"
                        }
                    },
                    "required": ["context", "treatment", "outcome"]
                },
                handler=self._handle_analyze_treatment_effect
            ),
            
            "create_causal_core": MCPTool(
                name="create_causal_core",
                description="Create a complete CausalLLM core instance for complex analysis",
                input_schema={
                    "type": "object", 
                    "properties": {
                        "context": {
                            "type": "string",
                            "description": "The system context description"
                        },
                        "variables": {
                            "type": "object",
                            "description": "Dictionary mapping variable names to descriptions"
                        },
                        "dag_edges": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 2,
                                "maxItems": 2
                            },
                            "description": "Causal DAG edges as [source, target] pairs"
                        }
                    },
                    "required": ["context", "variables", "dag_edges"]
                },
                handler=self._handle_create_causal_core
            )
        }
    
    def get_tool_list(self) -> List[Dict[str, Any]]:
        """Get list of available tools in MCP format."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            }
            for tool in self.tools.values()
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool with given arguments."""
        logger.info(f"Calling tool: {name}")
        
        if name not in self.tools:
            logger.error(f"Unknown tool: {name}")
            raise ValueError(f"Unknown tool: {name}")
        
        try:
            tool = self.tools[name]
            result = await tool.handler(arguments)
            
            logger.info(f"Tool {name} completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Tool {name} failed: {e}")
            raise RuntimeError(f"Tool execution failed: {e}")
    
    # Tool handler methods
    
    async def _handle_simulate_counterfactual(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle counterfactual simulation requests."""
        logger.debug("Handling counterfactual simulation")
        
        try:
            result = await asyncio.to_thread(
                self.counterfactual_engine.simulate_counterfactual,
                context=args["context"],
                factual=args["factual"], 
                intervention=args["intervention"],
                instruction=args.get("instruction"),
                temperature=args.get("temperature", 0.7),
                chain_of_thought=args.get("chain_of_thought", False)
            )
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Counterfactual simulation failed: {e}")
            return {
                "content": [
                    {
                        "type": "text", 
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def _handle_generate_do_prompt(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle do-calculus prompt generation."""
        logger.debug("Handling do-calculus prompt generation")
        
        try:
            do_operator = DoOperatorSimulator(
                base_context=args["context"],
                variables=args["variables"]
            )
            
            result = await asyncio.to_thread(
                do_operator.generate_do_prompt,
                interventions=args["intervention"],
                question=args.get("question")
            )
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Do-calculus prompt generation failed: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def _handle_extract_causal_edges(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle causal edge extraction."""
        logger.debug("Handling causal edge extraction")
        
        try:
            edges = await asyncio.to_thread(
                self.scm_explainer.extract_variables_and_edges,
                scenario_description=args["scenario_description"]
            )
            
            # Format edges as readable text
            if edges:
                edges_text = "\n".join([f"{source} → {target}" for source, target in edges])
                result_text = f"Extracted causal relationships:\n{edges_text}"
            else:
                result_text = "No clear causal relationships found in the description."
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result_text
                    }
                ],
                "edges": edges  # Include raw data for programmatic use
            }
            
        except Exception as e:
            logger.error(f"Causal edge extraction failed: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def _handle_generate_reasoning_prompt(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle reasoning prompt generation from DAG."""
        logger.debug("Handling reasoning prompt generation")
        
        try:
            # Convert edge list to tuples
            edges = [tuple(edge) for edge in args["dag_edges"]]
            
            dag_parser = DAGParser(edges)
            
            result = await asyncio.to_thread(
                dag_parser.to_prompt,
                task=args.get("task", "")
            )
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Reasoning prompt generation failed: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def _handle_analyze_treatment_effect(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle treatment effect analysis."""
        logger.debug("Handling treatment effect analysis")
        
        try:
            result = await asyncio.to_thread(
                PromptTemplates.treatment_effect_estimation,
                context=args["context"],
                treatment=args["treatment"],
                outcome=args["outcome"]
            )
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Treatment effect analysis failed: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def _handle_create_causal_core(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle causal core creation and provide access info.""" 
        logger.debug("Handling causal core creation")
        
        try:
            # Convert edge list to tuples
            edges = [tuple(edge) for edge in args["dag_edges"]]
            
            # Create core instance (this demonstrates the capability)
            core = CausalLLMCore(
                context=args["context"],
                variables=args["variables"], 
                dag_edges=edges,
                llm_client=self.llm_client
            )
            
            # Provide summary information
            result_text = f"""
Causal Core Instance Created Successfully:

Context: {args['context'][:200]}{'...' if len(args['context']) > 200 else ''}

Variables ({len(args['variables'])}):
{chr(10).join([f"- {name}: {desc}" for name, desc in args['variables'].items()])}

DAG Structure ({len(edges)} edges):
{chr(10).join([f"- {source} → {target}" for source, target in edges])}

Available Operations:
- simulate_do(): Apply do-calculus interventions
- simulate_counterfactual(): Run counterfactual analysis  
- generate_reasoning_prompt(): Create reasoning prompts

Use other MCP tools to interact with this causal model.
"""
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result_text
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Causal core creation failed: {e}")
            return {
                "content": [
                    {
                        "type": "text", 
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }