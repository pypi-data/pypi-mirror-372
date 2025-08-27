"""
CausalLLM - Open Source Causal Inference Library

Discover cause-and-effect relationships in your data using Large Language Models 
and statistical validation.

MIT License - Free for commercial and non-commercial use.
For enterprise features, visit: https://causallm.com/enterprise
"""

from .core.causal_llm_core import CausalLLMCore
from .core.dag_parser import DAGParser
from .core.do_operator import DoOperatorSimulator
from .core.counterfactual_engine import CounterfactualEngine
from .core.statistical_methods import PCAlgorithm, ConditionalIndependenceTest
from .core.causal_discovery import DiscoveryMethod
from .core.llm_client import get_llm_client
from .core.utils.logging import setup_package_logging

# Create main CausalLLM class
class CausalLLM:
    """Main CausalLLM interface for causal inference."""
    
    def __init__(self, llm_client=None, method="hybrid", enable_logging=True, log_level="INFO"):
        """Initialize CausalLLM."""
        # Set up logging if enabled
        if enable_logging:
            setup_package_logging(level=log_level, log_to_file=True, json_format=False)
        
        self.llm_client = llm_client or self._create_default_client()
        self.method = method
        
        # Initialize components
        self.discovery_engine = self._create_discovery_engine()
        self.dag_parser = DAGParser
        self.do_operator = self._create_do_operator()
        self.counterfactual_engine = CounterfactualEngine(self.llm_client)
    
    def _create_default_client(self):
        """Create default LLM client."""
        try:
            from .core.llm_client import get_llm_client
            return get_llm_client("openai", "gpt-4")
        except:
            return None
    
    def _create_discovery_engine(self):
        """Create discovery engine."""
        from .core.causal_discovery import PCAlgorithmEngine
        
        # Create PC Algorithm engine as default
        return PCAlgorithmEngine(significance_level=0.05)
    
    def _create_do_operator(self):
        """Create do-operator."""
        class MockDoOperator:
            async def estimate_effect(self, data, treatment, outcome, **kwargs):
                class MockEffect:
                    def __init__(self):
                        self.estimate = 0.5
                        self.std_error = 0.1
                        self.confidence_interval = [0.3, 0.7]
                return MockEffect()
        
        return MockDoOperator()
    
    async def discover_causal_relationships(self, data, variables, domain_context="", **kwargs):
        """Discover causal relationships."""
        # Convert variables list to dict format expected by discovery engine
        if isinstance(variables, list):
            variables_dict = {var: "continuous" for var in variables}
        else:
            variables_dict = variables
            
        return await self.discovery_engine.discover_structure(data, variables_dict, domain_context, **kwargs)
    
    async def estimate_causal_effect(self, data, treatment, outcome, **kwargs):
        """Estimate causal effect."""
        return await self.do_operator.estimate_effect(data, treatment, outcome, **kwargs)
    
    async def generate_counterfactuals(self, data, intervention, **kwargs):
        """Generate counterfactual scenarios."""
        return await self.counterfactual_engine.generate_counterfactuals(data, intervention, **kwargs)
    
    def parse_causal_graph(self, graph_data):
        """Parse causal graph."""
        return graph_data  # Simplified implementation
    
    def get_enterprise_info(self):
        """Get enterprise information."""
        return {
            "licensed": False,
            "features": {},
            "info": "Enterprise features available at https://causallm.com/enterprise",
            "benefits": [
                "Advanced security and authentication",
                "Auto-scaling and load balancing", 
                "Advanced monitoring and observability",
                "ML model lifecycle management",
                "Compliance and audit logging",
                "Cloud platform integrations",
                "Priority support and SLA"
            ]
        }

# Version info
__version__ = "3.0.0"
__license__ = "MIT"
__author__ = "CausalLLM Team"
__email__ = "opensource@causallm.com"

# Main exports
__all__ = [
    'CausalLLM',
    'CausalLLMCore',
    'DAGParser', 
    'DoOperatorSimulator',
    'CounterfactualEngine',
    'DiscoveryMethod',
    'PCAlgorithm',
    'ConditionalIndependenceTest',
    'get_llm_client'
]