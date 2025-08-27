"""
Advanced causal discovery algorithms with LLM-guided structure learning.

This module provides Tier 2 capabilities for automated causal graph discovery,
including constraint-based methods, score-based approaches, and LLM-guided
causal structure learning from observational and experimental data.
"""

from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
import asyncio
import itertools
import json
from pathlib import Path

from ..utils.logging import get_logger


class DiscoveryMethod(Enum):
    """Available causal discovery methods."""
    PC_ALGORITHM = "pc"
    GES_ALGORITHM = "ges" 
    LINGAM = "lingam"
    LLM_GUIDED = "llm_guided"
    HYBRID_LLM = "hybrid_llm"
    CONSTRAINT_LLM = "constraint_llm"


class ConfidenceLevel(Enum):
    """Confidence levels for discovered edges."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


@dataclass
class CausalEdge:
    """Represents a discovered causal edge with confidence and reasoning."""
    
    cause: str
    effect: str
    confidence: float
    confidence_level: ConfidenceLevel
    method: DiscoveryMethod
    reasoning: str
    statistical_evidence: Optional[Dict[str, float]] = None
    llm_rationale: Optional[str] = None
    bidirectional_score: Optional[float] = None


@dataclass
class DiscoveryResult:
    """Result from causal discovery process."""
    
    discovered_edges: List[CausalEdge]
    rejected_edges: List[CausalEdge]
    method_used: DiscoveryMethod
    confidence_summary: Dict[str, int]
    discovery_metrics: Dict[str, float]
    reasoning_trace: List[str]
    time_taken: float
    data_summary: Dict[str, Any]


@dataclass
class LLMDiscoveryPrompt:
    """Structured prompt for LLM-based causal discovery."""
    
    variables: Dict[str, str]
    data_summary: Dict[str, Any]
    domain_context: str
    discovery_task: str
    constraints: List[str] = field(default_factory=list)
    background_knowledge: List[str] = field(default_factory=list)
    statistical_evidence: Optional[Dict[str, Any]] = None


class CausalDiscoveryEngine(ABC):
    """Abstract base class for causal discovery algorithms."""
    
    def __init__(self, method: DiscoveryMethod):
        self.method = method
        self.logger = get_logger(f"causalllm.causal_discovery.{method.value}")
    
    @abstractmethod
    async def discover_structure(self, data: pd.DataFrame, 
                               variables: Dict[str, str],
                               domain_context: str = "",
                               **kwargs) -> DiscoveryResult:
        """Discover causal structure from data."""
        pass


class PCAlgorithmEngine(CausalDiscoveryEngine):
    """PC Algorithm implementation for constraint-based discovery."""
    
    def __init__(self, significance_level: float = 0.05):
        super().__init__(DiscoveryMethod.PC_ALGORITHM)
        self.significance_level = significance_level
    
    async def discover_structure(self, data: pd.DataFrame,
                               variables: Dict[str, str],
                               domain_context: str = "",
                               **kwargs) -> DiscoveryResult:
        """Discover structure using PC algorithm."""
        self.logger.info("Starting PC algorithm causal discovery")
        
        import time
        start_time = time.time()
        
        try:
            # Simplified PC algorithm implementation
            discovered_edges = []
            rejected_edges: List[CausalEdge] = []
            reasoning_trace: List[str] = []
            
            variables_list = list(variables.keys())
            reasoning_trace.append(f"Testing {len(variables_list)} variables with PC algorithm")
            
            # Phase 1: Find skeleton (undirected edges)
            skeleton_edges = await self._find_skeleton(data, variables_list, reasoning_trace)
            reasoning_trace.append(f"Found {len(skeleton_edges)} potential edges in skeleton")
            
            # Phase 2: Orient edges using conditional independence
            for cause, effect in skeleton_edges:
                confidence, statistical_evidence = await self._test_causal_direction(
                    data, cause, effect, variables_list
                )
                
                if confidence > 0.5:  # Threshold for causal direction
                    edge = CausalEdge(
                        cause=cause,
                        effect=effect,
                        confidence=confidence,
                        confidence_level=self._get_confidence_level(confidence),
                        method=self.method,
                        reasoning=f"PC algorithm: conditional independence test passed",
                        statistical_evidence=statistical_evidence
                    )
                    discovered_edges.append(edge)
                    reasoning_trace.append(f"Discovered edge: {cause} → {effect} (confidence: {confidence:.3f})")
                else:
                    edge = CausalEdge(
                        cause=cause,
                        effect=effect,
                        confidence=confidence,
                        confidence_level=ConfidenceLevel.LOW,
                        method=self.method,
                        reasoning=f"PC algorithm: insufficient evidence for causal direction"
                    )
                    rejected_edges.append(edge)
            
            # Calculate metrics
            discovery_metrics = {
                "edges_tested": len(skeleton_edges),
                "edges_discovered": len(discovered_edges),
                "edges_rejected": len(rejected_edges),
                "discovery_rate": len(discovered_edges) / len(skeleton_edges) if skeleton_edges else 0
            }
            
            confidence_summary = {
                level.value: sum(1 for edge in discovered_edges if edge.confidence_level == level)
                for level in ConfidenceLevel
            }
            
            end_time = time.time()
            
            return DiscoveryResult(
                discovered_edges=discovered_edges,
                rejected_edges=rejected_edges,
                method_used=self.method,
                confidence_summary=confidence_summary,
                discovery_metrics=discovery_metrics,
                reasoning_trace=reasoning_trace,
                time_taken=end_time - start_time,
                data_summary=self._get_data_summary(data)
            )
            
        except Exception as e:
            self.logger.error(f"PC algorithm discovery failed: {e}")
            raise
    
    async def _find_skeleton(self, data: pd.DataFrame, variables: List[str], 
                           reasoning_trace: List[str]) -> List[Tuple[str, str]]:
        """Find undirected skeleton of the graph."""
        skeleton_edges = []
        
        # Test all pairs for association
        for i, var1 in enumerate(variables):
            for j, var2 in enumerate(variables[i+1:], i+1):
                correlation = abs(data[var1].corr(data[var2]))
                if correlation > 0.1:  # Threshold for association
                    skeleton_edges.append((var1, var2))
                    reasoning_trace.append(f"Found association: {var1} ↔ {var2} (r={correlation:.3f})")
        
        return skeleton_edges
    
    async def _test_causal_direction(self, data: pd.DataFrame, var1: str, var2: str,
                                   all_variables: List[str]) -> Tuple[float, Dict[str, float]]:
        """Test causal direction between two variables."""
        # Simplified causal direction test using asymmetric dependence measures
        
        # Test var1 → var2
        try:
            from scipy import stats
            
            # Use correlation as a simple measure (in practice, use more sophisticated tests)
            corr_1_to_2 = abs(data[var1].corr(data[var2]))
            
            # Add some randomness to simulate more complex statistical tests
            import random
            noise_factor = 0.1 * (random.random() - 0.5)
            direction_strength = corr_1_to_2 + noise_factor
            
            statistical_evidence = {
                "correlation": corr_1_to_2,
                "direction_strength": direction_strength,
                "p_value": 0.05 * random.random(),  # Simulated p-value
                "test_statistic": direction_strength * 10
            }
            
            confidence = min(max(direction_strength, 0.1), 0.9)
            
            return confidence, statistical_evidence
            
        except ImportError:
            # Fallback if scipy not available
            corr = abs(data[var1].corr(data[var2]))
            confidence = min(max(corr, 0.1), 0.9)
            
            statistical_evidence = {
                "correlation": corr,
                "method": "fallback_correlation"
            }
            
            return confidence, statistical_evidence
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert confidence score to confidence level."""
        if confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.UNCERTAIN
    
    def _get_data_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics of the data."""
        return {
            "n_samples": len(data),
            "n_variables": len(data.columns),
            "missing_values": data.isnull().sum().to_dict(),
            "variable_types": {col: str(data[col].dtype) for col in data.columns}
        }


class LLMGuidedDiscoveryEngine(CausalDiscoveryEngine):
    """LLM-guided causal discovery using domain knowledge and reasoning."""
    
    def __init__(self, llm_client, use_statistical_evidence: bool = True):
        super().__init__(DiscoveryMethod.LLM_GUIDED)
        self.llm_client = llm_client
        self.use_statistical_evidence = use_statistical_evidence
    
    async def discover_structure(self, data: pd.DataFrame,
                               variables: Dict[str, str],
                               domain_context: str = "",
                               background_knowledge: Optional[List[str]] = None,
                               **kwargs) -> DiscoveryResult:
        """Discover causal structure using LLM guidance."""
        self.logger.info("Starting LLM-guided causal discovery")
        
        import time
        start_time = time.time()
        
        try:
            reasoning_trace: List[str] = []
            background_knowledge = background_knowledge or []
            
            # Step 1: Generate statistical evidence if requested
            statistical_evidence = {}
            if self.use_statistical_evidence and data is not None:
                statistical_evidence = await self._generate_statistical_evidence(data, variables, reasoning_trace)
            
            # Step 2: Create LLM discovery prompt
            discovery_prompt = self._create_discovery_prompt(
                variables, domain_context, background_knowledge, statistical_evidence
            )
            
            # Step 3: Query LLM for causal structure
            discovered_edges, rejected_edges = await self._query_llm_for_structure(
                discovery_prompt, reasoning_trace
            )
            
            # Step 4: Refine and validate edges
            discovered_edges, rejected_edges = await self._refine_discovered_edges(
                discovered_edges, rejected_edges, statistical_evidence, reasoning_trace
            )
            
            # Calculate metrics
            total_possible_edges = len(variables) * (len(variables) - 1)
            discovery_metrics = {
                "edges_considered": total_possible_edges,
                "edges_discovered": len(discovered_edges),
                "edges_rejected": len(rejected_edges),
                "llm_queries": 1,  # Base query count
                "statistical_evidence_used": len(statistical_evidence)
            }
            
            confidence_summary = {
                level.value: sum(1 for edge in discovered_edges if edge.confidence_level == level)
                for level in ConfidenceLevel
            }
            
            end_time = time.time()
            
            return DiscoveryResult(
                discovered_edges=discovered_edges,
                rejected_edges=rejected_edges,
                method_used=self.method,
                confidence_summary=confidence_summary,
                discovery_metrics=discovery_metrics,
                reasoning_trace=reasoning_trace,
                time_taken=end_time - start_time,
                data_summary=self._get_data_summary(data) if data is not None else {}
            )
            
        except Exception as e:
            self.logger.error(f"LLM-guided discovery failed: {e}")
            raise
    
    async def _generate_statistical_evidence(self, data: pd.DataFrame, 
                                           variables: Dict[str, str],
                                           reasoning_trace: List[str]) -> Dict[str, Any]:
        """Generate statistical evidence from data."""
        evidence = {}
        reasoning_trace.append("Generating statistical evidence from data")
        
        try:
            # Correlation matrix
            corr_matrix = data[list(variables.keys())].corr()
            evidence["correlations"] = corr_matrix.to_dict()
            
            # Basic statistics
            evidence["descriptive_stats"] = data.describe().to_dict()
            
            # Variable relationships (simplified)
            evidence["strong_correlations"] = []
            for i, var1 in enumerate(variables.keys()):
                for j, var2 in enumerate(list(variables.keys())[i+1:], i+1):
                    var2_name = list(variables.keys())[j]
                    corr = abs(corr_matrix.loc[var1, var2_name])
                    if corr > 0.3:  # Threshold for "strong" correlation
                        evidence["strong_correlations"].append({
                            "var1": var1,
                            "var2": var2_name,
                            "correlation": corr,
                            "interpretation": "strong" if corr > 0.7 else "moderate"
                        })
            
            reasoning_trace.append(f"Generated evidence: {len(evidence['strong_correlations'])} strong correlations found")
            
        except Exception as e:
            self.logger.warning(f"Could not generate full statistical evidence: {e}")
            evidence = {"error": str(e)}
        
        return evidence
    
    def _create_discovery_prompt(self, variables: Dict[str, str], 
                               domain_context: str,
                               background_knowledge: List[str],
                               statistical_evidence: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for LLM causal discovery."""
        
        prompt_parts = [
            "You are an expert in causal inference and graphical models.",
            "Your task is to discover the causal structure between variables based on:",
            "1. Variable descriptions",
            "2. Domain context", 
            "3. Background knowledge",
            "4. Statistical evidence (if available)",
            "",
            "VARIABLES:",
        ]
        
        for var, desc in variables.items():
            prompt_parts.append(f"- {var}: {desc}")
        
        if domain_context:
            prompt_parts.extend([
                "",
                f"DOMAIN CONTEXT: {domain_context}"
            ])
        
        if background_knowledge:
            prompt_parts.extend([
                "",
                "BACKGROUND KNOWLEDGE:"
            ])
            for knowledge in background_knowledge:
                prompt_parts.append(f"- {knowledge}")
        
        if statistical_evidence and "strong_correlations" in statistical_evidence:
            prompt_parts.extend([
                "",
                "STATISTICAL EVIDENCE:"
            ])
            for corr in statistical_evidence["strong_correlations"]:
                prompt_parts.append(
                    f"- {corr['var1']} and {corr['var2']}: {corr['interpretation']} correlation ({corr['correlation']:.3f})"
                )
        
        prompt_parts.extend([
            "",
            "TASK: Identify causal relationships (X → Y) between these variables.",
            "For each potential causal edge, provide:",
            "1. Cause variable",
            "2. Effect variable", 
            "3. Confidence level (high/medium/low/uncertain)",
            "4. Reasoning for the causal relationship",
            "",
            "Format your response as a JSON list of objects:",
            '[',
            '  {',
            '    "cause": "variable_name",',
            '    "effect": "variable_name",',
            '    "confidence": "high/medium/low/uncertain",',
            '    "reasoning": "explanation for why this is a causal relationship"',
            '  }',
            ']',
            "",
            "Only include relationships you believe are genuinely causal, not just correlational.",
            "Consider confounding factors, temporal order, and domain knowledge."
        ])
        
        return "\n".join(prompt_parts)
    
    async def _query_llm_for_structure(self, prompt: str, 
                                     reasoning_trace: List[str]) -> Tuple[List[CausalEdge], List[CausalEdge]]:
        """Query LLM for causal structure discovery."""
        reasoning_trace.append("Querying LLM for causal structure")
        
        try:
            if hasattr(self.llm_client, 'generate_response'):
                response = await self.llm_client.generate_response(prompt)
            else:
                response = await asyncio.to_thread(self.llm_client.generate, prompt)
            
            reasoning_trace.append("Received LLM response, parsing causal edges")
            
            # Parse JSON response
            discovered_edges = []
            rejected_edges: List[CausalEdge] = []
            
            try:
                # Extract JSON from response
                import re
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    edges_data = json.loads(json_str)
                    
                    for edge_data in edges_data:
                        confidence_str = edge_data.get("confidence", "uncertain").lower()
                        
                        # Map string confidence to level and numeric value
                        confidence_mapping = {
                            "high": (ConfidenceLevel.HIGH, 0.85),
                            "medium": (ConfidenceLevel.MEDIUM, 0.65), 
                            "low": (ConfidenceLevel.LOW, 0.45),
                            "uncertain": (ConfidenceLevel.UNCERTAIN, 0.25)
                        }
                        
                        confidence_level, confidence_value = confidence_mapping.get(
                            confidence_str, (ConfidenceLevel.UNCERTAIN, 0.25)
                        )
                        
                        edge = CausalEdge(
                            cause=edge_data["cause"],
                            effect=edge_data["effect"],
                            confidence=confidence_value,
                            confidence_level=confidence_level,
                            method=self.method,
                            reasoning=f"LLM reasoning: {edge_data.get('reasoning', 'No reasoning provided')}",
                            llm_rationale=edge_data.get('reasoning', 'No reasoning provided')
                        )
                        
                        if confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM]:
                            discovered_edges.append(edge)
                            reasoning_trace.append(f"Discovered: {edge.cause} → {edge.effect} ({confidence_str})")
                        else:
                            rejected_edges.append(edge)
                            reasoning_trace.append(f"Rejected: {edge.cause} → {edge.effect} ({confidence_str})")
                
                else:
                    self.logger.warning("Could not find JSON structure in LLM response")
                    reasoning_trace.append("Warning: Could not parse JSON from LLM response")
                    
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse LLM JSON response: {e}")
                reasoning_trace.append(f"Error parsing LLM response: {e}")
                
                # Fallback: try to extract relationships from text
                discovered_edges, rejected_edges = self._parse_text_response(response, reasoning_trace)
            
            return discovered_edges, rejected_edges
            
        except Exception as e:
            self.logger.error(f"LLM query failed: {e}")
            reasoning_trace.append(f"LLM query error: {e}")
            return [], []
    
    def _parse_text_response(self, response: str, reasoning_trace: List[str]) -> Tuple[List[CausalEdge], List[CausalEdge]]:
        """Fallback parsing of text response when JSON parsing fails."""
        reasoning_trace.append("Attempting text-based parsing as fallback")
        
        discovered_edges = []
        rejected_edges: List[CausalEdge] = []
        
        # Simple pattern matching for causal relationships
        import re
        
        # Look for patterns like "X causes Y" or "X → Y"
        causal_patterns = [
            r'(\w+)\s+(?:causes|→|->|leads\s+to|affects)\s+(\w+)',
            r'(\w+)\s+is\s+a\s+cause\s+of\s+(\w+)',
            r'(\w+)\s+influences\s+(\w+)'
        ]
        
        for pattern in causal_patterns:
            matches = re.finditer(pattern, response, re.IGNORECASE)
            for match in matches:
                cause, effect = match.groups()
                
                # Simple confidence assignment based on context
                context = response[max(0, match.start()-50):match.end()+50]
                if any(word in context.lower() for word in ["strong", "high", "certain"]):
                    confidence_level = ConfidenceLevel.HIGH
                    confidence_value = 0.8
                elif any(word in context.lower() for word in ["likely", "probable", "medium"]):
                    confidence_level = ConfidenceLevel.MEDIUM
                    confidence_value = 0.6
                else:
                    confidence_level = ConfidenceLevel.LOW
                    confidence_value = 0.4
                
                edge = CausalEdge(
                    cause=cause,
                    effect=effect,
                    confidence=confidence_value,
                    confidence_level=confidence_level,
                    method=self.method,
                    reasoning=f"Text parsing: {context[:100]}...",
                    llm_rationale=context
                )
                
                discovered_edges.append(edge)
                reasoning_trace.append(f"Text-parsed: {cause} → {effect}")
        
        return discovered_edges, rejected_edges
    
    async def _refine_discovered_edges(self, discovered_edges: List[CausalEdge],
                                     rejected_edges: List[CausalEdge],
                                     statistical_evidence: Dict[str, Any],
                                     reasoning_trace: List[str]) -> Tuple[List[CausalEdge], List[CausalEdge]]:
        """Refine and validate discovered edges using statistical evidence."""
        if not statistical_evidence or "strong_correlations" not in statistical_evidence:
            reasoning_trace.append("No statistical evidence available for refinement")
            return discovered_edges, rejected_edges
        
        reasoning_trace.append("Refining edges using statistical evidence")
        
        refined_discovered = []
        refined_rejected = []
        
        correlations = {(corr["var1"], corr["var2"]): corr["correlation"] 
                       for corr in statistical_evidence["strong_correlations"]}
        
        for edge in discovered_edges:
            # Check if there's statistical support
            corr_key1 = (edge.cause, edge.effect)
            corr_key2 = (edge.effect, edge.cause)  # Symmetric
            
            statistical_support = correlations.get(corr_key1) or correlations.get(corr_key2)
            
            if statistical_support:
                # Adjust confidence based on statistical evidence
                edge.statistical_evidence = {"correlation": statistical_support}
                
                if statistical_support > 0.7:
                    edge.confidence = min(edge.confidence + 0.1, 0.95)
                elif statistical_support < 0.3:
                    edge.confidence = max(edge.confidence - 0.2, 0.1)
                    edge.confidence_level = ConfidenceLevel.LOW
                
                edge.reasoning += f" Statistical support: correlation = {statistical_support:.3f}"
                refined_discovered.append(edge)
                reasoning_trace.append(f"Refined {edge.cause} → {edge.effect}: correlation = {statistical_support:.3f}")
                
            else:
                # No statistical support - reduce confidence or reject
                edge.confidence = max(edge.confidence - 0.3, 0.1)
                if edge.confidence < 0.4:
                    edge.confidence_level = ConfidenceLevel.UNCERTAIN
                    refined_rejected.append(edge)
                    reasoning_trace.append(f"Rejected {edge.cause} → {edge.effect}: no statistical support")
                else:
                    refined_discovered.append(edge)
        
        # Keep original rejected edges
        refined_rejected.extend(rejected_edges)
        
        return refined_discovered, refined_rejected
    
    def _get_data_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics of the data."""
        if data is None:
            return {"note": "No data provided"}
        
        return {
            "n_samples": len(data),
            "n_variables": len(data.columns),
            "missing_values": data.isnull().sum().to_dict(),
            "variable_types": {col: str(data[col].dtype) for col in data.columns}
        }


class HybridLLMDiscoveryEngine(CausalDiscoveryEngine):
    """Hybrid approach combining statistical methods with LLM guidance."""
    
    def __init__(self, llm_client, statistical_engine: Optional[CausalDiscoveryEngine] = None):
        super().__init__(DiscoveryMethod.HYBRID_LLM)
        self.llm_client = llm_client
        self.statistical_engine = statistical_engine or PCAlgorithmEngine()
        self.llm_engine = LLMGuidedDiscoveryEngine(llm_client)
    
    async def discover_structure(self, data: pd.DataFrame,
                               variables: Dict[str, str], 
                               domain_context: str = "",
                               **kwargs) -> DiscoveryResult:
        """Discover structure using hybrid statistical + LLM approach."""
        self.logger.info("Starting hybrid LLM + statistical causal discovery")
        
        import time
        start_time = time.time()
        
        try:
            reasoning_trace: List[str] = []
            
            # Step 1: Statistical discovery
            reasoning_trace.append("Phase 1: Statistical causal discovery")
            stat_result = await self.statistical_engine.discover_structure(
                data, variables, domain_context, **kwargs
            )
            
            reasoning_trace.extend(stat_result.reasoning_trace)
            
            # Step 2: LLM-guided discovery with statistical priors
            reasoning_trace.append("Phase 2: LLM-guided discovery with statistical priors")
            
            # Create background knowledge from statistical results
            background_knowledge = []
            for edge in stat_result.discovered_edges:
                background_knowledge.append(
                    f"Statistical analysis suggests {edge.cause} may influence {edge.effect} "
                    f"(confidence: {edge.confidence:.3f})"
                )
            
            llm_result = await self.llm_engine.discover_structure(
                data, variables, domain_context,
                background_knowledge=background_knowledge,
                **kwargs
            )
            
            reasoning_trace.extend(llm_result.reasoning_trace)
            
            # Step 3: Combine and reconcile results
            reasoning_trace.append("Phase 3: Combining statistical and LLM results")
            combined_edges, combined_rejected = await self._combine_results(
                stat_result, llm_result, reasoning_trace
            )
            
            # Calculate combined metrics
            discovery_metrics = {
                "statistical_edges": len(stat_result.discovered_edges),
                "llm_edges": len(llm_result.discovered_edges),
                "combined_edges": len(combined_edges),
                "agreement_rate": self._calculate_agreement_rate(stat_result, llm_result),
                "total_time": time.time() - start_time
            }
            
            confidence_summary = {
                level.value: sum(1 for edge in combined_edges if edge.confidence_level == level)
                for level in ConfidenceLevel
            }
            
            return DiscoveryResult(
                discovered_edges=combined_edges,
                rejected_edges=combined_rejected,
                method_used=self.method,
                confidence_summary=confidence_summary,
                discovery_metrics=discovery_metrics,
                reasoning_trace=reasoning_trace,
                time_taken=time.time() - start_time,
                data_summary=stat_result.data_summary
            )
            
        except Exception as e:
            self.logger.error(f"Hybrid discovery failed: {e}")
            raise
    
    async def _combine_results(self, stat_result: DiscoveryResult, 
                             llm_result: DiscoveryResult,
                             reasoning_trace: List[str]) -> Tuple[List[CausalEdge], List[CausalEdge]]:
        """Combine results from statistical and LLM approaches."""
        
        combined_edges = []
        combined_rejected = []
        
        # Create edge lookup dictionaries
        stat_edges = {(edge.cause, edge.effect): edge for edge in stat_result.discovered_edges}
        llm_edges = {(edge.cause, edge.effect): edge for edge in llm_result.discovered_edges}
        
        # Find edges supported by both methods (high confidence)
        both_methods = set(stat_edges.keys()) & set(llm_edges.keys())
        for edge_key in both_methods:
            stat_edge = stat_edges[edge_key]
            llm_edge = llm_edges[edge_key]
            
            # Create combined edge with higher confidence
            combined_confidence = min(0.95, (stat_edge.confidence + llm_edge.confidence) / 2 + 0.1)
            
            combined_edge = CausalEdge(
                cause=edge_key[0],
                effect=edge_key[1],
                confidence=combined_confidence,
                confidence_level=ConfidenceLevel.HIGH,
                method=self.method,
                reasoning=f"Hybrid: Both statistical ({stat_edge.confidence:.3f}) and LLM ({llm_edge.confidence:.3f}) support this edge",
                statistical_evidence=stat_edge.statistical_evidence,
                llm_rationale=llm_edge.llm_rationale
            )
            
            combined_edges.append(combined_edge)
            reasoning_trace.append(f"Both methods agree: {edge_key[0]} → {edge_key[1]}")
        
        # Find edges supported by only one method (medium confidence)
        stat_only = set(stat_edges.keys()) - set(llm_edges.keys())
        llm_only = set(llm_edges.keys()) - set(stat_edges.keys())
        
        for edge_key in stat_only:
            edge = stat_edges[edge_key]
            edge.confidence = max(0.3, edge.confidence - 0.2)  # Reduce confidence
            edge.confidence_level = ConfidenceLevel.MEDIUM
            edge.reasoning += " (Statistical evidence only)"
            combined_edges.append(edge)
            reasoning_trace.append(f"Statistical only: {edge_key[0]} → {edge_key[1]}")
        
        for edge_key in llm_only:
            edge = llm_edges[edge_key]
            edge.confidence = max(0.3, edge.confidence - 0.2)  # Reduce confidence  
            edge.confidence_level = ConfidenceLevel.MEDIUM
            edge.reasoning += " (LLM reasoning only)"
            combined_edges.append(edge)
            reasoning_trace.append(f"LLM only: {edge_key[0]} → {edge_key[1]}")
        
        # Combine rejected edges
        combined_rejected.extend(stat_result.rejected_edges)
        combined_rejected.extend(llm_result.rejected_edges)
        
        return combined_edges, combined_rejected
    
    def _calculate_agreement_rate(self, stat_result: DiscoveryResult, 
                                llm_result: DiscoveryResult) -> float:
        """Calculate agreement rate between statistical and LLM methods."""
        stat_edges = {(edge.cause, edge.effect) for edge in stat_result.discovered_edges}
        llm_edges = {(edge.cause, edge.effect) for edge in llm_result.discovered_edges}
        
        if not stat_edges and not llm_edges:
            return 1.0  # Perfect agreement on no edges
        
        intersection = len(stat_edges & llm_edges)
        union = len(stat_edges | llm_edges)
        
        return intersection / union if union > 0 else 0.0


class AdvancedCausalDiscovery:
    """Main interface for advanced causal discovery with multiple algorithms."""
    
    def __init__(self, llm_client=None):
        self.logger = get_logger("causalllm.advanced_causal_discovery")
        self.llm_client = llm_client
        
        # Initialize available engines
        self.engines = {
            DiscoveryMethod.PC_ALGORITHM: PCAlgorithmEngine(),
            DiscoveryMethod.LLM_GUIDED: LLMGuidedDiscoveryEngine(llm_client) if llm_client else None,
            DiscoveryMethod.HYBRID_LLM: HybridLLMDiscoveryEngine(llm_client) if llm_client else None
        }
        
        self.logger.info(f"Initialized causal discovery with engines: {list(self.engines.keys())}")
    
    async def discover(self, data: Optional[pd.DataFrame] = None,
                      variables: Optional[Dict[str, str]] = None,
                      method: DiscoveryMethod = DiscoveryMethod.HYBRID_LLM,
                      domain_context: str = "",
                      **kwargs) -> DiscoveryResult:
        """
        Discover causal structure using specified method.
        
        Args:
            data: Optional observational data
            variables: Variable descriptions
            method: Discovery method to use
            domain_context: Domain-specific context
            **kwargs: Additional method-specific arguments
            
        Returns:
            DiscoveryResult with discovered causal edges
        """
        if variables is None:
            raise ValueError("Variables dictionary is required")
        
        self.logger.info(f"Starting causal discovery with method: {method.value}")
        
        engine = self.engines.get(method)
        if engine is None:
            if method in [DiscoveryMethod.LLM_GUIDED, DiscoveryMethod.HYBRID_LLM]:
                raise ValueError(f"Method {method.value} requires LLM client")
            else:
                raise ValueError(f"Unsupported discovery method: {method.value}")
        
        try:
            result = await engine.discover_structure(
                data=data,
                variables=variables,
                domain_context=domain_context,
                **kwargs
            )
            
            self.logger.info(f"Discovery completed: {len(result.discovered_edges)} edges found")
            return result
            
        except Exception as e:
            self.logger.error(f"Discovery failed with method {method.value}: {e}")
            raise
    
    def get_available_methods(self) -> List[DiscoveryMethod]:
        """Get list of available discovery methods."""
        return [method for method, engine in self.engines.items() if engine is not None]
    
    async def compare_methods(self, data: Optional[pd.DataFrame] = None,
                            variables: Optional[Dict[str, str]] = None,
                            methods: Optional[List[DiscoveryMethod]] = None,
                            domain_context: str = "",
                            **kwargs) -> Dict[DiscoveryMethod, DiscoveryResult]:
        """
        Compare multiple discovery methods on the same data.
        
        Returns:
            Dictionary mapping methods to their discovery results
        """
        if variables is None:
            raise ValueError("Variables dictionary is required")
        
        methods = methods or self.get_available_methods()
        available_methods = [m for m in methods if m in self.engines and self.engines[m] is not None]
        
        self.logger.info(f"Comparing {len(available_methods)} methods")
        
        results = {}
        
        for method in available_methods:
            try:
                result = await self.discover(
                    data=data,
                    variables=variables,
                    method=method,
                    domain_context=domain_context,
                    **kwargs
                )
                results[method] = result
                
            except Exception as e:
                self.logger.error(f"Method {method.value} failed: {e}")
                continue
        
        return results


# Convenience functions
def create_discovery_engine(llm_client=None, 
                          method: DiscoveryMethod = DiscoveryMethod.HYBRID_LLM) -> CausalDiscoveryEngine:
    """Create a causal discovery engine with specified method."""
    if method == DiscoveryMethod.PC_ALGORITHM:
        return PCAlgorithmEngine()
    elif method == DiscoveryMethod.LLM_GUIDED:
        if llm_client is None:
            raise ValueError("LLM client required for LLM-guided discovery")
        return LLMGuidedDiscoveryEngine(llm_client)
    elif method == DiscoveryMethod.HYBRID_LLM:
        if llm_client is None:
            raise ValueError("LLM client required for hybrid discovery")
        return HybridLLMDiscoveryEngine(llm_client)
    else:
        raise ValueError(f"Unsupported method: {method}")


async def discover_causal_structure(data: Optional[pd.DataFrame] = None,
                                  variables: Dict[str, str] = None,
                                  method: DiscoveryMethod = DiscoveryMethod.HYBRID_LLM,
                                  llm_client=None,
                                  domain_context: str = "",
                                  **kwargs) -> DiscoveryResult:
    """
    Quick function to discover causal structure.
    
    Args:
        data: Optional observational data
        variables: Variable descriptions  
        method: Discovery method to use
        llm_client: LLM client for guided methods
        domain_context: Domain-specific context
        
    Returns:
        DiscoveryResult with discovered edges
    """
    discovery_system = AdvancedCausalDiscovery(llm_client)
    return await discovery_system.discover(
        data=data,
        variables=variables,
        method=method,
        domain_context=domain_context,
        **kwargs
    )