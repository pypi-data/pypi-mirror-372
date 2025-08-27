"""
Enhanced CausalLLM - Comprehensive Causal Inference Platform

This module provides the main enhanced CausalLLM interface that combines
statistical methods with LLM-powered domain knowledge for robust causal analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import warnings

from .core.enhanced_causal_discovery import (
    EnhancedCausalDiscovery, 
    CausalDiscoveryResult,
    CausalEdge
)
from .core.statistical_inference import (
    StatisticalCausalInference,
    CausalInferenceResult,
    CausalEffect,
    CausalMethod
)
from .core.llm_client import get_llm_client

warnings.filterwarnings('ignore')

@dataclass 
class ComprehensiveCausalAnalysis:
    """Complete causal analysis result combining discovery and inference."""
    discovery_results: CausalDiscoveryResult
    inference_results: Dict[str, CausalInferenceResult]
    domain_recommendations: str
    methodology_assessment: str
    actionable_insights: List[str]
    confidence_score: float

class EnhancedCausalLLM:
    """
    Enhanced CausalLLM platform providing comprehensive causal analysis capabilities.
    
    This class combines:
    - Automated causal structure discovery
    - Multiple statistical inference methods  
    - LLM-powered domain expertise
    - Assumption testing and validation
    - Actionable business insights
    """
    
    def __init__(self, llm_provider: str = "openai", llm_model: str = "gpt-4", 
                 significance_level: float = 0.05):
        """
        Initialize Enhanced CausalLLM.
        
        Args:
            llm_provider: LLM provider ("openai", "llama", "grok", "mcp")
            llm_model: Specific model to use
            significance_level: Statistical significance level for tests
        """
        
        # Initialize LLM client
        try:
            self.llm_client = get_llm_client(llm_provider, llm_model)
            self.llm_available = True
        except Exception as e:
            print(f"Warning: LLM client initialization failed: {e}")
            print("Falling back to statistical methods only.")
            self.llm_client = None
            self.llm_available = False
        
        # Initialize core engines
        self.discovery_engine = EnhancedCausalDiscovery(
            llm_client=self.llm_client, 
            significance_level=significance_level
        )
        
        self.inference_engine = StatisticalCausalInference(
            significance_level=significance_level
        )
        
        self.significance_level = significance_level
    
    def discover_causal_relationships(self, data: pd.DataFrame, 
                                    variables: List[str] = None,
                                    domain: str = None) -> CausalDiscoveryResult:
        """
        Discover causal relationships in data using hybrid statistical-LLM approach.
        
        Args:
            data: Input dataset
            variables: Variables to analyze (if None, uses all columns)
            domain: Domain context ('healthcare', 'marketing', 'finance', etc.)
            
        Returns:
            CausalDiscoveryResult with discovered relationships and insights
        """
        
        print("🔍 " + "="*60)
        print("   ENHANCED CAUSAL DISCOVERY")
        print("="*63)
        print()
        
        # Validate input data
        self._validate_data(data, variables)
        
        # Discover causal structure
        discovery_results = self.discovery_engine.discover_causal_structure(
            data, variables, domain
        )
        
        # Print summary
        print(f"✅ Discovery complete!")
        print(f"   • Found {len(discovery_results.discovered_edges)} causal relationships")
        print(f"   • Domain: {discovery_results.statistical_summary['domain']}")
        print(f"   • High confidence edges: {discovery_results.statistical_summary['high_confidence_relationships']}")
        print()
        
        return discovery_results
    
    def estimate_causal_effect(self, data: pd.DataFrame,
                              treatment: str,
                              outcome: str,
                              covariates: List[str] = None,
                              method: str = "comprehensive",
                              instrument: str = None) -> CausalInferenceResult:
        """
        Estimate causal effect using statistical methods.
        
        Args:
            data: Input dataset
            treatment: Treatment/intervention variable
            outcome: Outcome variable  
            covariates: List of control variables
            method: Method to use ("regression", "matching", "iv", "comprehensive")
            instrument: Instrumental variable (for IV estimation)
            
        Returns:
            CausalInferenceResult with effect estimates and analysis
        """
        
        print("📊 " + "="*60)
        print("   CAUSAL EFFECT ESTIMATION")
        print("="*63)
        print()
        
        # Validate inputs
        self._validate_treatment_outcome(data, treatment, outcome, covariates)
        
        if method == "comprehensive":
            # Comprehensive analysis with multiple methods
            inference_results = self.inference_engine.comprehensive_causal_analysis(
                data, treatment, outcome, covariates, instrument
            )
        else:
            # Single method analysis
            method_mapping = {
                "regression": CausalMethod.LINEAR_REGRESSION,
                "matching": CausalMethod.MATCHING,
                "iv": CausalMethod.INSTRUMENTAL_VARIABLES
            }
            
            causal_method = method_mapping.get(method, CausalMethod.LINEAR_REGRESSION)
            primary_effect = self.inference_engine.estimate_causal_effect(
                data, treatment, outcome, covariates, causal_method, instrument
            )
            
            # Create comprehensive result with single method
            inference_results = CausalInferenceResult(
                primary_effect=primary_effect,
                robustness_checks=[],
                sensitivity_analysis={},
                recommendations=f"Single method analysis using {method}",
                confidence_level="Medium" if primary_effect.p_value < 0.05 else "Low",
                overall_assessment=primary_effect.interpretation
            )
        
        # Print summary  
        print(f"✅ Effect estimation complete!")
        print(f"   • Primary effect: {inference_results.primary_effect.effect_estimate:.4f}")
        print(f"   • P-value: {inference_results.primary_effect.p_value:.4f}")
        print(f"   • Confidence: {inference_results.confidence_level}")
        print(f"   • Robustness checks: {len(inference_results.robustness_checks)}")
        print()
        
        return inference_results
    
    def comprehensive_analysis(self, data: pd.DataFrame,
                              treatment: str = None,
                              outcome: str = None,
                              variables: List[str] = None,
                              domain: str = None,
                              covariates: List[str] = None) -> ComprehensiveCausalAnalysis:
        """
        Perform comprehensive causal analysis combining discovery and inference.
        
        Args:
            data: Input dataset
            treatment: Primary treatment variable (if None, will be inferred)
            outcome: Primary outcome variable (if None, will be inferred)  
            variables: Variables to include in analysis
            domain: Domain context
            covariates: Control variables
            
        Returns:
            ComprehensiveCausalAnalysis with complete analysis results
        """
        
        print("🚀 " + "="*60)
        print("   COMPREHENSIVE CAUSAL ANALYSIS")
        print("="*63)
        print()
        
        # Step 1: Causal Discovery
        print("Phase 1: Causal Structure Discovery")
        discovery_results = self.discover_causal_relationships(data, variables, domain)
        
        # Step 2: Identify key relationships for detailed analysis
        inference_results = {}
        
        if treatment and outcome:
            # Analyze specified treatment-outcome relationship
            print(f"Phase 2: Analyzing {treatment} → {outcome}")
            inference_results[f"{treatment}_to_{outcome}"] = self.estimate_causal_effect(
                data, treatment, outcome, covariates, "comprehensive"
            )
        else:
            # Analyze top discovered relationships
            top_edges = sorted(discovery_results.discovered_edges, 
                             key=lambda x: x.confidence, reverse=True)[:3]
            
            print("Phase 2: Analyzing Top Discovered Relationships")
            for i, edge in enumerate(top_edges):
                if edge.confidence >= 0.6:  # Only analyze high-confidence relationships
                    print(f"   Analyzing relationship {i+1}: {edge.cause} → {edge.effect}")
                    inference_results[f"{edge.cause}_to_{edge.effect}"] = self.estimate_causal_effect(
                        data, edge.cause, edge.effect, covariates, "comprehensive"
                    )
        
        # Step 3: Generate domain recommendations
        domain_recommendations = self._generate_domain_recommendations(
            discovery_results, inference_results, domain
        )
        
        # Step 4: Methodology assessment
        methodology_assessment = self._assess_methodology(
            discovery_results, inference_results
        )
        
        # Step 5: Extract actionable insights
        actionable_insights = self._extract_actionable_insights(
            discovery_results, inference_results, domain
        )
        
        # Step 6: Calculate overall confidence score
        confidence_score = self._calculate_overall_confidence(
            discovery_results, inference_results
        )
        
        print("✅ Comprehensive analysis complete!")
        print(f"   • Overall confidence: {confidence_score:.2f}")
        print(f"   • Actionable insights: {len(actionable_insights)}")
        print()
        
        return ComprehensiveCausalAnalysis(
            discovery_results=discovery_results,
            inference_results=inference_results,
            domain_recommendations=domain_recommendations,
            methodology_assessment=methodology_assessment,
            actionable_insights=actionable_insights,
            confidence_score=confidence_score
        )
    
    def generate_intervention_recommendations(self, analysis: ComprehensiveCausalAnalysis,
                                           target_outcome: str,
                                           budget_constraint: float = None) -> Dict[str, Any]:
        """
        Generate specific intervention recommendations based on causal analysis.
        
        Args:
            analysis: Results from comprehensive_analysis()
            target_outcome: Desired outcome to optimize
            budget_constraint: Maximum budget for interventions
            
        Returns:
            Dictionary with intervention recommendations and expected impacts
        """
        
        print("💡 Generating intervention recommendations...")
        
        recommendations = {
            'primary_interventions': [],
            'secondary_interventions': [],
            'expected_impacts': {},
            'implementation_priority': [],
            'risk_assessment': {}
        }
        
        # Find causal relationships affecting target outcome
        relevant_edges = []
        
        for edge in analysis.discovery_results.discovered_edges:
            if edge.effect.lower() == target_outcome.lower():
                relevant_edges.append(edge)
        
        # Add from inference results
        for key, result in analysis.inference_results.items():
            if result.primary_effect.outcome.lower() == target_outcome.lower():
                # Create synthetic edge from inference result
                synthetic_edge = type('Edge', (), {
                    'cause': result.primary_effect.treatment,
                    'effect': result.primary_effect.outcome,
                    'confidence': result.primary_effect.robustness_score,
                    'effect_size': abs(result.primary_effect.effect_estimate),
                    'interpretation': result.primary_effect.interpretation
                })
                relevant_edges.append(synthetic_edge)
        
        # Sort by potential impact (confidence * effect_size)
        relevant_edges.sort(key=lambda x: x.confidence * getattr(x, 'effect_size', 0), reverse=True)
        
        # Generate recommendations
        for i, edge in enumerate(relevant_edges[:5]):  # Top 5 interventions
            intervention = {
                'target_variable': edge.cause,
                'expected_outcome_change': getattr(edge, 'effect_size', 'moderate'),
                'confidence_level': edge.confidence,
                'implementation_complexity': 'medium',  # Default
                'estimated_cost': 'TBD',
                'timeline': '3-6 months',
                'success_metrics': [f"Change in {edge.effect}", f"Improvement in {edge.cause}"]
            }
            
            if i < 2:
                recommendations['primary_interventions'].append(intervention)
            else:
                recommendations['secondary_interventions'].append(intervention)
        
        return recommendations
    
    def _validate_data(self, data: pd.DataFrame, variables: List[str] = None):
        """Validate input data for analysis."""
        if data.empty:
            raise ValueError("Input data cannot be empty")
        
        if len(data) < 50:
            print("Warning: Small sample size (n < 50). Results may be unreliable.")
        
        if variables:
            missing_vars = [v for v in variables if v not in data.columns]
            if missing_vars:
                raise ValueError(f"Variables not found in data: {missing_vars}")
    
    def _validate_treatment_outcome(self, data: pd.DataFrame, treatment: str, 
                                   outcome: str, covariates: List[str] = None):
        """Validate treatment and outcome variables."""
        if treatment not in data.columns:
            raise ValueError(f"Treatment variable '{treatment}' not found in data")
        
        if outcome not in data.columns:
            raise ValueError(f"Outcome variable '{outcome}' not found in data")
        
        if covariates:
            missing_covs = [c for c in covariates if c not in data.columns]
            if missing_covs:
                raise ValueError(f"Covariates not found in data: {missing_covs}")
    
    def _generate_domain_recommendations(self, discovery: CausalDiscoveryResult,
                                       inference: Dict[str, CausalInferenceResult],
                                       domain: str) -> str:
        """Generate domain-specific recommendations."""
        
        recommendations = f"# {domain.title() if domain else 'General'} Domain Recommendations\n\n"
        
        # High-impact relationships
        high_impact = [edge for edge in discovery.discovered_edges if edge.confidence >= 0.8]
        
        if high_impact:
            recommendations += "## High-Impact Causal Relationships\n"
            for edge in high_impact[:3]:
                recommendations += f"- **{edge.cause} → {edge.effect}**: {edge.interpretation}\n"
            recommendations += "\n"
        
        # Statistical inference insights
        if inference:
            recommendations += "## Key Quantitative Findings\n"
            for key, result in inference.items():
                if result.primary_effect.p_value < 0.05:
                    recommendations += f"- **{result.primary_effect.treatment}**: "
                    recommendations += f"{result.primary_effect.interpretation}\n"
            recommendations += "\n"
        
        # Domain-specific advice
        if domain == 'healthcare':
            recommendations += "## Clinical Implementation Guidelines\n"
            recommendations += "- Validate findings through randomized controlled trials\n"
            recommendations += "- Consider patient heterogeneity and subgroup effects\n"
            recommendations += "- Monitor for adverse effects and unintended consequences\n"
            recommendations += "- Implement gradual rollout with continuous monitoring\n"
        elif domain == 'marketing':
            recommendations += "## Marketing Strategy Implementation\n"
            recommendations += "- Test interventions through controlled A/B experiments\n"
            recommendations += "- Segment customers for personalized approaches\n"
            recommendations += "- Monitor long-term customer lifetime value impacts\n"
            recommendations += "- Account for competitive responses and market changes\n"
        elif domain == 'finance':
            recommendations += "## Financial Strategy Considerations\n"
            recommendations += "- Validate relationships across different market conditions\n"
            recommendations += "- Implement risk management protocols\n"
            recommendations += "- Monitor for regime changes and structural breaks\n"
            recommendations += "- Consider regulatory and compliance implications\n"
        
        return recommendations
    
    def _assess_methodology(self, discovery: CausalDiscoveryResult,
                           inference: Dict[str, CausalInferenceResult]) -> str:
        """Assess the methodology used and provide quality metrics."""
        
        assessment = "# Methodology Assessment\n\n"
        
        # Discovery assessment
        assessment += "## Causal Discovery Quality\n"
        assessment += f"- **Relationships discovered**: {len(discovery.discovered_edges)}\n"
        assessment += f"- **High confidence edges**: {discovery.statistical_summary['high_confidence_relationships']}\n"
        assessment += f"- **Average effect size**: {discovery.statistical_summary['average_effect_size']:.3f}\n"
        
        if discovery.assumptions_violated:
            assessment += f"- **Assumptions violated**: {len(discovery.assumptions_violated)}\n"
            for violation in discovery.assumptions_violated:
                assessment += f"  - {violation}\n"
        
        assessment += "\n"
        
        # Inference assessment
        if inference:
            assessment += "## Statistical Inference Quality\n"
            
            total_methods = sum(1 + len(result.robustness_checks) for result in inference.values())
            significant_results = sum(
                (1 if result.primary_effect.p_value < 0.05 else 0) + 
                len([r for r in result.robustness_checks if r.p_value < 0.05])
                for result in inference.values()
            )
            
            assessment += f"- **Total methods applied**: {total_methods}\n"
            assessment += f"- **Significant results**: {significant_results}\n"
            assessment += f"- **Consistency rate**: {significant_results/total_methods*100:.1f}%\n"
            
            # Method-specific insights
            method_counts = {}
            for result in inference.values():
                method = result.primary_effect.method
                method_counts[method] = method_counts.get(method, 0) + 1
                
                for rob in result.robustness_checks:
                    method = rob.method
                    method_counts[method] = method_counts.get(method, 0) + 1
            
            assessment += "\n**Methods used:**\n"
            for method, count in method_counts.items():
                assessment += f"- {method.replace('_', ' ').title()}: {count} applications\n"
        
        return assessment
    
    def _extract_actionable_insights(self, discovery: CausalDiscoveryResult,
                                   inference: Dict[str, CausalInferenceResult],
                                   domain: str) -> List[str]:
        """Extract actionable insights from the analysis."""
        
        insights = []
        
        # From discovery results
        for edge in discovery.discovered_edges:
            if edge.confidence >= 0.7:
                insights.append(
                    f"Focus on {edge.cause} to improve {edge.effect} "
                    f"(confidence: {edge.confidence:.2f})"
                )
        
        # From inference results
        for key, result in inference.items():
            if result.primary_effect.p_value < 0.05:
                effect_size = abs(result.primary_effect.effect_estimate)
                if effect_size >= 0.3:
                    insights.append(
                        f"Strong intervention opportunity: {result.primary_effect.treatment} "
                        f"can change {result.primary_effect.outcome} by {effect_size:.2f} units"
                    )
        
        # Domain-specific insights
        if domain == 'healthcare' and discovery.suggested_confounders:
            insights.append(
                "Control for patient demographics and comorbidities in treatment decisions"
            )
        elif domain == 'marketing':
            insights.append(
                "Test multi-channel approaches for synergistic effects on customer engagement"
            )
        elif domain == 'finance':
            insights.append(
                "Monitor macroeconomic indicators as leading factors for portfolio decisions"
            )
        
        return insights[:10]  # Return top 10 insights
    
    def _calculate_overall_confidence(self, discovery: CausalDiscoveryResult,
                                    inference: Dict[str, CausalInferenceResult]) -> float:
        """Calculate overall confidence score for the analysis."""
        
        # Discovery confidence component
        if discovery.discovered_edges:
            avg_discovery_confidence = np.mean([edge.confidence for edge in discovery.discovered_edges])
        else:
            avg_discovery_confidence = 0.0
        
        # Inference confidence component
        if inference:
            inference_confidences = []
            for result in inference.values():
                # Convert p-value to confidence score
                primary_conf = max(0, 1 - result.primary_effect.p_value * 20)
                inference_confidences.append(primary_conf)
                
                # Add robustness check confidences
                for rob in result.robustness_checks:
                    rob_conf = max(0, 1 - rob.p_value * 20)
                    inference_confidences.append(rob_conf)
            
            avg_inference_confidence = np.mean(inference_confidences) if inference_confidences else 0.0
        else:
            avg_inference_confidence = 0.0
        
        # Sample size adjustment
        sample_size_factor = min(1.0, discovery.statistical_summary['total_relationships_tested'] / 100)
        
        # Overall confidence
        overall_confidence = (
            0.4 * avg_discovery_confidence + 
            0.4 * avg_inference_confidence + 
            0.2 * sample_size_factor
        )
        
        return overall_confidence