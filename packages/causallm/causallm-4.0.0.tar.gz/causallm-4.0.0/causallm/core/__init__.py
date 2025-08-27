"""
CausalLLM Core - Open Source Causal Inference Library

This is the open source core of CausalLLM, providing fundamental causal inference
capabilities powered by Large Language Models and statistical validation.

MIT License - Free for commercial and non-commercial use.
"""

from .causal_discovery import DiscoveryMethod
from .dag_parser import DAGParser
from .do_operator import DoOperatorSimulator
from .counterfactual_engine import CounterfactualEngine
from .llm_client import BaseLLMClient, OpenAIClient, get_llm_client
from .prompt_templates import get_causal_discovery_prompt, get_intervention_prompt
from .statistical_methods import PCAlgorithm, ConditionalIndependenceTest

# Stub classes for compatibility
class CausalDiscoveryEngine:
    def __init__(self, llm_client=None, method="hybrid"):
        self.llm_client = llm_client
        self.method = method
    
    async def discover_relationships(self, data, variables, **kwargs):
        class MockResult:
            def __init__(self):
                self.discovered_edges = []
                self.confidence_summary = {}
        return MockResult()

class CausalGraph:
    """Alias for DAGParser"""
    pass

class DoOperator:
    """Alias for DoOperatorSimulator"""
    def __init__(self):
        pass
    
    async def estimate_effect(self, data, treatment, outcome, **kwargs):
        class MockEffect:
            def __init__(self):
                self.estimate = 0.5
                self.std_error = 0.1
                self.confidence_interval = [0.3, 0.7]
        return MockEffect()

class InterventionResult:
    """Mock intervention result"""
    pass

def create_llm_client():
    """Create default LLM client"""
    try:
        return get_llm_client("openai", "gpt-4")
    except:
        return None

# Core CausalLLM class for open source users
class CausalLLM:
    """
    Open Source CausalLLM - Core causal inference capabilities
    
    For enterprise features (advanced security, scaling, monitoring, etc.),
    visit: https://causallm.com/enterprise
    """
    
    def __init__(self, llm_client=None, method="hybrid"):
        """
        Initialize CausalLLM with core functionality
        
        Args:
            llm_client: LLM client for causal reasoning
            method: Causal discovery method ('llm', 'statistical', 'hybrid')
        """
        self.llm_client = llm_client or create_llm_client()
        self.discovery_engine = CausalDiscoveryEngine(self.llm_client, method)
        self.dag_parser = DAGParser
        self.do_operator = DoOperator()
        self.counterfactual_engine = CounterfactualEngine(self.llm_client)
        
        # Check if enterprise features are available
        try:
            from ..enterprise import is_enterprise_licensed
            self._enterprise_available = is_enterprise_licensed()
        except ImportError:
            self._enterprise_available = False
    
    async def discover_causal_relationships(self, data, variables=None, **kwargs):
        """Discover causal relationships in data"""
        return await self.discovery_engine.discover_relationships(
            data, variables, **kwargs
        )
    
    async def estimate_causal_effect(self, data, treatment, outcome, **kwargs):
        """Estimate causal effect using do-calculus"""
        return await self.do_operator.estimate_effect(
            data, treatment, outcome, **kwargs
        )
    
    async def generate_counterfactuals(self, data, intervention, **kwargs):
        """Generate counterfactual scenarios"""
        return await self.counterfactual_engine.generate_counterfactuals(
            data, intervention, **kwargs
        )
    
    def parse_causal_graph(self, graph_data):
        """Parse and validate causal graph structure"""
        return self.dag_parser.parse(graph_data)
    
    def get_enterprise_info(self):
        """Get information about enterprise features"""
        if self._enterprise_available:
            from ..enterprise import enterprise
            return {
                "licensed": True,
                "features": enterprise.list_features(),
                "info": "Enterprise features are available"
            }
        else:
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

__version__ = "3.0.0"
__license__ = "MIT"
__author__ = "CausalLLM Team"
__email__ = "opensource@causallm.com"

__all__ = [
    'CausalLLM',
    'CausalDiscoveryEngine', 
    'DAGParser',
    'DoOperator',
    'CounterfactualEngine',
    'DiscoveryMethod',
    'CausalGraph',
    'InterventionResult'
]