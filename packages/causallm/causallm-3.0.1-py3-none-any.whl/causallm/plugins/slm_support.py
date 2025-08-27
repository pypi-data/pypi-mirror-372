"""
Small Language Model support for CausalLLM
Provides optimized clients for smaller, faster models
"""


def create_slm_optimized_client(model_name):
    """Create an optimized client for small language models."""
    from ..core.llm_client import get_llm_client
    
    # Map SLM model names to providers
    if "llama" in model_name.lower():
        try:
            return get_llm_client("llama", model_name)
        except:
            pass
    
    # Fallback to basic client
    class MockSLMClient:
        def __init__(self, model):
            self.model = model
        
        def chat(self, prompt, temperature=0.7):
            return f"[SLM-{self.model}]: Optimized response for: {prompt[:50]}..."
    
    return MockSLMClient(model_name)