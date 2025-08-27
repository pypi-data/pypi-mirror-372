"""
Small Language Model Client Implementation for CausalLLM
Provides optimized support for local and lightweight language models
"""

import os
import time
import json
import logging
import hashlib
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from dataclasses import dataclass
from functools import lru_cache

from causalllm.logging import get_logger

class ModelSize(Enum):
    TINY = "tiny"      # <2B parameters
    SMALL = "small"    # 2B-7B parameters  
    MEDIUM = "medium"  # 7B-13B parameters
    LARGE = "large"    # 13B+ parameters

@dataclass
class SLMConfig:
    """Configuration for Small Language Models"""
    model_name: str
    size: ModelSize
    max_tokens: int = 2048
    context_length: int = 4096
    requires_gpu: bool = False
    memory_gb: float = 4.0
    inference_speed_factor: float = 1.0  # Relative to GPT-3.5

class OllamaClient:
    """Ollama client for local small language model inference"""
    
    def __init__(self, 
                 model: str = "llama2:7b-chat",
                 base_url: str = "http://localhost:11434",
                 timeout: int = 120):
        self.logger = get_logger("causalllm.llm_client.ollama")
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        
        # Response cache for frequently asked questions
        self.response_cache: Dict[str, str] = {}
        
        try:
            import requests
            self.requests = requests
            
            # Test connection and model availability
            self._test_connection()
            self.logger.info(f"Ollama client initialized with model: {model}")
            
        except ImportError:
            self.logger.error("requests package required for Ollama client")
            raise ImportError("Please install requests: pip install requests")
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama client: {e}")
            raise
    
    def _test_connection(self):
        """Test connection to Ollama server"""
        try:
            response = self.requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                available_models = [model["name"] for model in response.json().get("models", [])]
                if self.model not in available_models:
                    self.logger.warning(f"Model {self.model} not found. Available: {available_models}")
                    self.logger.info(f"Pulling model {self.model}...")
                    self._pull_model()
            else:
                raise ConnectionError(f"Ollama server responded with status {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Failed to connect to Ollama server at {self.base_url}: {e}")
            raise
    
    def _pull_model(self):
        """Pull model if not available locally"""
        try:
            response = self.requests.post(
                f"{self.base_url}/api/pull",
                json={"name": self.model},
                timeout=300  # 5 minutes for model download
            )
            
            if response.status_code == 200:
                self.logger.info(f"Successfully pulled model {self.model}")
            else:
                self.logger.error(f"Failed to pull model {self.model}")
                
        except Exception as e:
            self.logger.error(f"Error pulling model: {e}")
    
    def chat(self, prompt: str, model: str = "", temperature: float = 0.7) -> str:
        """Generate response using Ollama"""
        if not prompt or not prompt.strip():
            self.logger.error("Empty prompt provided")
            raise ValueError("Prompt cannot be empty")
        
        use_model = model or self.model
        
        # Check cache first
        cache_key = self._get_cache_key(prompt, use_model, temperature)
        if cache_key in self.response_cache:
            self.logger.debug("Returning cached response")
            return self.response_cache[cache_key]
        
        # Optimize prompt for small models
        optimized_prompt = self._optimize_prompt_for_slm(prompt)
        
        self.logger.info(f"Generating response with {use_model}")
        self.logger.debug(f"Optimized prompt length: {len(optimized_prompt)}")
        
        start_time = time.time()
        try:
            response = self.requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": use_model,
                    "prompt": optimized_prompt,
                    "options": {
                        "temperature": temperature,
                        "num_predict": 1024,  # Limit tokens for faster response
                        "top_k": 40,
                        "top_p": 0.9,
                        "repeat_penalty": 1.1,
                        "stop": ["</analysis>", "###", "---"]  # Stop sequences
                    },
                    "stream": False
                },
                timeout=self.timeout
            )
            
            duration = time.time() - start_time
            response.raise_for_status()
            
            result = response.json()
            
            if "response" in result:
                generated_text = result["response"].strip()
                
                # Cache successful responses
                self.response_cache[cache_key] = generated_text
                
                # Limit cache size
                if len(self.response_cache) > 100:
                    # Remove oldest entries (simple FIFO)
                    oldest_key = next(iter(self.response_cache))
                    del self.response_cache[oldest_key]
                
                self.logger.info(f"Response generated in {duration:.2f}s")
                return generated_text
            else:
                raise ValueError("Invalid response format from Ollama")
                
        except Exception as e:
            self.logger.error(f"Ollama generation failed: {e}")
            raise RuntimeError(f"Failed to generate response: {e}")
    
    def _get_cache_key(self, prompt: str, model: str, temperature: float) -> str:
        """Generate cache key for prompt"""
        content = f"{prompt}|{model}|{temperature:.2f}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _optimize_prompt_for_slm(self, prompt: str) -> str:
        """Optimize prompt for small language models"""
        
        # Detect if this is a causal analysis prompt
        is_causal = any(keyword in prompt.lower() for keyword in 
                       ['causal', 'cause', 'effect', 'relationship', 'influence'])
        
        if is_causal:
            # Structure causal analysis prompts better for SLMs
            if "analyze" in prompt.lower() or "find" in prompt.lower():
                structured_prompt = self._structure_causal_prompt(prompt)
                return structured_prompt
        
        # General optimizations for small models
        optimized = prompt
        
        # Simplify complex instructions
        simplifications = {
            "Please carefully analyze": "Analyze",
            "I would like you to": "",
            "Could you please": "",
            "It would be helpful if you could": "",
            "Take your time to": "",
            "Please provide a detailed": "Provide a",
            "comprehensive analysis": "analysis"
        }
        
        for old, new in simplifications.items():
            optimized = optimized.replace(old, new)
        
        # Add structure for better performance
        if len(optimized) > 500:
            # Break long prompts into sections
            optimized = f"Task: {optimized[:200]}...\n\nInstructions:\n{optimized[200:]}"
        
        return optimized.strip()
    
    def _structure_causal_prompt(self, prompt: str) -> str:
        """Structure causal analysis prompts for better SLM performance"""
        
        # Extract key components
        data_mention = "data" in prompt.lower()
        variables_mention = "variable" in prompt.lower()
        
        structured = "CAUSAL ANALYSIS TASK\n\n"
        
        if data_mention:
            structured += "Goal: Find cause-and-effect relationships in the data.\n"
        if variables_mention:
            structured += "Method: Look for variables that influence other variables.\n"
        
        structured += "\nRules:\n"
        structured += "- X causes Y if X happens before Y\n"
        structured += "- X causes Y if changing X changes Y\n"
        structured += "- Consider alternative explanations\n\n"
        
        structured += f"Analysis:\n{prompt}\n\n"
        structured += "Format your answer as: Variable1 → Variable2 (confidence: high/medium/low)\n"
        
        return structured

class LocalHFClient:
    """Local Hugging Face transformer client"""
    
    def __init__(self, 
                 model_name: str = "microsoft/DialoGPT-medium",
                 device: str = "auto",
                 load_in_8bit: bool = False):
        self.logger = get_logger("causalllm.llm_client.hf_local")
        self.model_name = model_name
        
        try:
            from transformers import pipeline, AutoTokenizer
            import torch
            
            # Determine device
            if device == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.logger.info(f"Auto-selected device: {device}")
            
            self.device = device
            
            self.logger.info(f"Loading {model_name} on {device}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Pipeline configuration
            pipeline_kwargs = {
                "model": model_name,
                "tokenizer": self.tokenizer,
                "device": 0 if device == "cuda" else -1,
                "return_full_text": False,
                "do_sample": True
            }
            
            if load_in_8bit and device != "cpu":
                pipeline_kwargs["model_kwargs"] = {"load_in_8bit": True}
                self.logger.info("Using 8-bit quantization")
            
            self.pipe = pipeline("text-generation", **pipeline_kwargs)
            self.logger.info("Model loaded successfully")
            
        except ImportError as e:
            self.logger.error("transformers and torch packages required for local HF models")
            raise ImportError("Please install: pip install transformers torch") from e
        except Exception as e:
            self.logger.error(f"Failed to load model {model_name}: {e}")
            raise
    
    def chat(self, prompt: str, model: str = "", temperature: float = 0.7) -> str:
        """Generate response using local HF model"""
        if not prompt or not prompt.strip():
            self.logger.error("Empty prompt provided")
            raise ValueError("Prompt cannot be empty")
        
        # Format prompt for chat models
        formatted_prompt = self._format_prompt_for_chat(prompt)
        
        self.logger.info(f"Generating response with {self.model_name}")
        
        try:
            # Generation parameters optimized for causal analysis
            generation_kwargs = {
                "max_new_tokens": 512,
                "temperature": temperature,
                "top_p": 0.9,
                "top_k": 50,
                "repetition_penalty": 1.1,
                "pad_token_id": self.tokenizer.eos_token_id,
                "eos_token_id": self.tokenizer.eos_token_id,
                "do_sample": temperature > 0
            }
            
            outputs = self.pipe(formatted_prompt, **generation_kwargs)
            
            if outputs and len(outputs) > 0:
                generated_text = outputs[0]['generated_text'].strip()
                
                # Post-process the output
                cleaned_text = self._clean_generated_text(generated_text)
                
                self.logger.info("Response generated successfully")
                return cleaned_text
            else:
                raise ValueError("Empty response from model")
                
        except Exception as e:
            self.logger.error(f"Local HF generation failed: {e}")
            raise RuntimeError(f"Failed to generate response: {e}")
    
    def _format_prompt_for_chat(self, prompt: str) -> str:
        """Format prompt for chat-based models"""
        
        # For chat models, use appropriate formatting
        if "chat" in self.model_name.lower() or "instruct" in self.model_name.lower():
            return f"<|user|>\n{prompt}\n<|assistant|>\n"
        
        # For general models, add context
        return f"Human: {prompt}\n\nAssistant: "
    
    def _clean_generated_text(self, text: str) -> str:
        """Clean and format generated text"""
        
        # Remove common artifacts
        text = text.replace("<|user|>", "").replace("<|assistant|>", "")
        text = text.replace("Human:", "").replace("Assistant:", "")
        
        # Remove excessive newlines
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        
        # Trim whitespace
        text = text.strip()
        
        return text

class SLMManager:
    """Manager class for Small Language Model operations"""
    
    def __init__(self):
        self.logger = get_logger("causalllm.slm_manager")
        self.available_clients = {}
        self.current_client = None
        
    def register_client(self, name: str, client):
        """Register an SLM client"""
        self.available_clients[name] = client
        self.logger.info(f"Registered SLM client: {name}")
    
    def set_active_client(self, name: str):
        """Set active SLM client"""
        if name not in self.available_clients:
            raise ValueError(f"Client {name} not registered")
        
        self.current_client = self.available_clients[name]
        self.logger.info(f"Active SLM client set to: {name}")
    
    def get_client_recommendations(self, use_case: str, memory_limit_gb: float = 8.0) -> List[str]:
        """Get recommended clients based on use case and resources"""
        
        recommendations = []
        
        use_case = use_case.lower()
        
        if memory_limit_gb >= 12:
            # Can handle larger models
            if "complex" in use_case or "detailed" in use_case:
                recommendations.extend(["ollama:llama2:13b", "ollama:mistral:7b"])
            else:
                recommendations.extend(["ollama:llama2:7b", "ollama:gemma:7b"])
        
        elif memory_limit_gb >= 6:
            # Medium models
            recommendations.extend(["ollama:llama2:7b", "ollama:mistral:7b", "hf:microsoft/Phi-3-mini-4k-instruct"])
        
        elif memory_limit_gb >= 3:
            # Small models
            recommendations.extend(["ollama:gemma:2b", "hf:microsoft/DialoGPT-medium"])
        
        else:
            # Very constrained
            recommendations.extend(["ollama:tinyllama", "hf:distilbert-base-uncased"])
        
        return recommendations
    
    def auto_select_client(self, use_case: str = "general", memory_limit_gb: float = 8.0):
        """Automatically select and configure the best available SLM client"""
        
        recommendations = self.get_client_recommendations(use_case, memory_limit_gb)
        
        for rec in recommendations:
            try:
                if rec.startswith("ollama:"):
                    model = rec.replace("ollama:", "")
                    client = OllamaClient(model=model)
                    self.register_client(f"ollama_{model.replace(':', '_')}", client)
                    self.set_active_client(f"ollama_{model.replace(':', '_')}")
                    return client
                
                elif rec.startswith("hf:"):
                    model = rec.replace("hf:", "")
                    client = LocalHFClient(model_name=model)
                    self.register_client(f"hf_{model.split('/')[-1]}", client)
                    self.set_active_client(f"hf_{model.split('/')[-1]}")
                    return client
                    
            except Exception as e:
                self.logger.warning(f"Failed to initialize {rec}: {e}")
                continue
        
        raise RuntimeError("No suitable SLM client could be initialized")
    
    def benchmark_clients(self, test_prompts: List[str]) -> Dict[str, Dict[str, float]]:
        """Benchmark available SLM clients"""
        
        results = {}
        
        for name, client in self.available_clients.items():
            self.logger.info(f"Benchmarking {name}")
            
            times = []
            success_count = 0
            
            for prompt in test_prompts:
                try:
                    start_time = time.time()
                    response = client.chat(prompt)
                    duration = time.time() - start_time
                    
                    if response and len(response) > 10:  # Valid response
                        times.append(duration)
                        success_count += 1
                        
                except Exception as e:
                    self.logger.warning(f"Benchmark failed for {name}: {e}")
            
            if times:
                results[name] = {
                    "avg_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "success_rate": success_count / len(test_prompts),
                    "total_tests": len(test_prompts)
                }
        
        return results

# Factory function for easy SLM client creation
def create_slm_client(provider: str = "auto", **kwargs):
    """Create optimized SLM client"""
    
    if provider == "auto":
        manager = SLMManager()
        return manager.auto_select_client(
            use_case=kwargs.get("use_case", "general"),
            memory_limit_gb=kwargs.get("memory_limit_gb", 8.0)
        )
    
    elif provider.lower() == "ollama":
        return OllamaClient(**kwargs)
    
    elif provider.lower() in ["huggingface", "hf"]:
        return LocalHFClient(**kwargs)
    
    else:
        raise ValueError(f"Unsupported SLM provider: {provider}")

# Integration with existing CausalLLM
def integrate_slm_with_causallm():
    """Integration helper for CausalLLM"""
    
    try:
        # Try to create an optimized SLM client
        slm_client = create_slm_client("auto", use_case="causal_analysis")
        
        return {
            "client": slm_client,
            "type": "SLM",
            "benefits": [
                "Faster inference (5-10x speedup)",
                "Lower costs (90%+ reduction)",
                "Complete data privacy",
                "No API dependencies"
            ],
            "limitations": [
                "Reduced accuracy for complex tasks",
                "Limited domain knowledge",
                "Requires local resources"
            ]
        }
        
    except Exception as e:
        logging.warning(f"SLM integration failed: {e}")
        return None

if __name__ == "__main__":
    # Demo usage
    print("🤖 CausalLLM Small Language Model Support Demo")
    
    try:
        # Auto-select best SLM
        slm_manager = SLMManager()
        client = slm_manager.auto_select_client("causal_analysis", memory_limit_gb=8)
        
        # Test causal analysis prompt
        test_prompt = """
        Analyze this data for causal relationships:
        Variables: marketing_spend, website_traffic, sales_revenue
        Data shows: When marketing_spend increases, website_traffic increases, then sales_revenue increases.
        Find: What causes what?
        """
        
        print("\n📊 Testing causal analysis with SLM...")
        response = client.chat(test_prompt, temperature=0.3)
        print(f"✅ Response: {response}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("💡 Try installing Ollama or Hugging Face transformers for SLM support")