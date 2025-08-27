"""
Enhanced Causal Discovery Engine

This module provides sophisticated causal discovery capabilities combining
LLM domain knowledge with statistical methods for robust causal structure learning.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import warnings
from scipy import stats
from itertools import combinations, permutations

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class ConfidenceLevel(Enum):
    """Confidence levels for causal relationships."""
    HIGH = "high"
    MEDIUM = "medium"  
    LOW = "low"

@dataclass
class CausalEdge:
    """Represents a discovered causal relationship."""
    cause: str
    effect: str
    confidence: float
    method: str
    p_value: float
    effect_size: float
    interpretation: str

@dataclass
class CausalDiscoveryResult:
    """Result of causal discovery analysis."""
    discovered_edges: List[CausalEdge]
    suggested_confounders: Dict[str, List[str]]
    assumptions_violated: List[str]
    domain_insights: str
    statistical_summary: Dict[str, Any]

class StatisticalCausalDiscovery:
    """Statistical methods for causal discovery."""
    
    def __init__(self, significance_level: float = 0.05):
        self.significance_level = significance_level
    
    def conditional_independence_test(self, data: pd.DataFrame, 
                                    x: str, y: str, 
                                    conditioning_set: List[str] = None) -> Tuple[float, float]:
        """
        Test conditional independence between X and Y given Z.
        Returns (test_statistic, p_value)
        """
        if conditioning_set is None:
            conditioning_set = []
        
        # For simplicity, using correlation-based tests
        # In production, would use more sophisticated methods like HSIC, FCIT
        
        try:
            if not conditioning_set:
                # Simple independence test
                if data[x].dtype in ['object', 'category'] or data[y].dtype in ['object', 'category']:
                    # Chi-square test for categorical variables
                    contingency_table = pd.crosstab(data[x], data[y])
                    chi2, p_value, _, _ = stats.chi2_contingency(contingency_table)
                    return chi2, p_value
                else:
                    # Pearson correlation test for continuous variables
                    corr, p_value = stats.pearsonr(data[x], data[y])
                    return abs(corr), p_value
            else:
                # Partial correlation test
                return self._partial_correlation_test(data, x, y, conditioning_set)
                
        except Exception as e:
            # Return non-significant result if test fails
            return 0.0, 1.0
    
    def _partial_correlation_test(self, data: pd.DataFrame, 
                                 x: str, y: str, 
                                 conditioning_set: List[str]) -> Tuple[float, float]:
        """Calculate partial correlation controlling for conditioning set."""
        try:
            # Simple implementation using linear regression residuals
            # In production, would use more sophisticated methods
            
            from sklearn.linear_model import LinearRegression
            
            # Convert categorical variables to dummy variables
            data_numeric = pd.get_dummies(data[[x, y] + conditioning_set], drop_first=True)
            
            if len(conditioning_set) == 0:
                corr, p_value = stats.pearsonr(data_numeric[x], data_numeric[y])
                return abs(corr), p_value
            
            # Get residuals after regressing on conditioning set
            conditioning_cols = [col for col in data_numeric.columns 
                               if any(cond in col for cond in conditioning_set)]
            
            if len(conditioning_cols) == 0:
                corr, p_value = stats.pearsonr(data_numeric[x], data_numeric[y])
                return abs(corr), p_value
            
            reg_x = LinearRegression().fit(data_numeric[conditioning_cols], data_numeric[x])
            reg_y = LinearRegression().fit(data_numeric[conditioning_cols], data_numeric[y])
            
            residuals_x = data_numeric[x] - reg_x.predict(data_numeric[conditioning_cols])
            residuals_y = data_numeric[y] - reg_y.predict(data_numeric[conditioning_cols])
            
            corr, p_value = stats.pearsonr(residuals_x, residuals_y)
            return abs(corr), p_value
            
        except Exception:
            return 0.0, 1.0
    
    def pc_algorithm_simple(self, data: pd.DataFrame, 
                           variables: List[str]) -> List[Tuple[str, str]]:
        """
        Simplified PC algorithm for causal structure learning.
        Returns list of potential causal edges.
        """
        edges = []
        
        # Start with complete graph
        potential_edges = list(permutations(variables, 2))
        
        # Remove edges based on conditional independence tests
        for x, y in potential_edges:
            # Test direct association
            _, p_direct = self.conditional_independence_test(data, x, y)
            
            if p_direct < self.significance_level:
                # Test with each other variable as conditioning set
                independent_given_others = False
                
                for z in variables:
                    if z != x and z != y:
                        _, p_conditional = self.conditional_independence_test(data, x, y, [z])
                        
                        if p_conditional >= self.significance_level:
                            independent_given_others = True
                            break
                
                # If not independent given any single variable, keep edge
                if not independent_given_others:
                    edges.append((x, y))
        
        return edges
    
    def calculate_effect_size(self, data: pd.DataFrame, 
                            cause: str, effect: str) -> float:
        """Calculate effect size between cause and effect."""
        try:
            if data[cause].dtype in ['object', 'category']:
                # For categorical causes, use eta-squared (effect size for ANOVA)
                groups = [data[data[cause] == cat][effect].dropna() 
                         for cat in data[cause].unique()]
                
                # Remove empty groups
                groups = [group for group in groups if len(group) > 0]
                
                if len(groups) < 2:
                    return 0.0
                
                f_stat, _ = stats.f_oneway(*groups)
                
                # Convert F-statistic to eta-squared approximation
                total_n = sum(len(group) for group in groups)
                between_df = len(groups) - 1
                eta_squared = (between_df * f_stat) / (between_df * f_stat + total_n - len(groups))
                return eta_squared
            else:
                # For continuous variables, use correlation coefficient
                corr, _ = stats.pearsonr(data[cause], data[effect])
                return abs(corr)
                
        except Exception:
            return 0.0

class LLMCausalAssistant:
    """LLM-powered causal reasoning assistant."""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.domain_knowledge = {
            'healthcare': {
                'common_causes': ['age', 'gender', 'socioeconomic_status', 'genetics', 'lifestyle'],
                'common_effects': ['mortality', 'recovery_time', 'complications', 'quality_of_life'],
                'known_relationships': [
                    ('age', 'complications'),
                    ('smoking', 'lung_disease'),
                    ('exercise', 'cardiovascular_health')
                ]
            },
            'marketing': {
                'common_causes': ['demographics', 'previous_behavior', 'seasonality', 'economic_factors'],
                'common_effects': ['conversion_rate', 'customer_lifetime_value', 'engagement'],
                'known_relationships': [
                    ('email_frequency', 'unsubscribe_rate'),
                    ('price', 'demand'),
                    ('advertising_spend', 'brand_awareness')
                ]
            },
            'finance': {
                'common_causes': ['market_conditions', 'company_fundamentals', 'macroeconomic_factors'],
                'common_effects': ['stock_price', 'volatility', 'returns'],
                'known_relationships': [
                    ('interest_rates', 'stock_prices'),
                    ('earnings', 'stock_price'),
                    ('market_volatility', 'risk_premium')
                ]
            }
        }
    
    def detect_domain(self, variables: List[str]) -> str:
        """Automatically detect domain based on variable names."""
        healthcare_terms = ['age', 'treatment', 'patient', 'diagnosis', 'recovery', 'mortality', 
                           'disease', 'symptom', 'medication', 'therapy', 'clinical']
        marketing_terms = ['conversion', 'campaign', 'customer', 'revenue', 'click', 'impression',
                          'engagement', 'channel', 'acquisition', 'retention']
        finance_terms = ['price', 'return', 'volatility', 'market', 'stock', 'bond', 'portfolio',
                        'risk', 'earnings', 'revenue', 'profit']
        
        variable_text = ' '.join(variables).lower()
        
        healthcare_score = sum(1 for term in healthcare_terms if term in variable_text)
        marketing_score = sum(1 for term in marketing_terms if term in variable_text)
        finance_score = sum(1 for term in finance_terms if term in variable_text)
        
        if healthcare_score >= marketing_score and healthcare_score >= finance_score:
            return 'healthcare'
        elif marketing_score >= finance_score:
            return 'marketing'
        else:
            return 'finance'
    
    def suggest_confounders(self, treatment: str, outcome: str, 
                          available_variables: List[str], domain: str = None) -> List[str]:
        """Suggest potential confounders based on domain knowledge."""
        if domain is None:
            domain = self.detect_domain([treatment, outcome] + available_variables)
        
        domain_info = self.domain_knowledge.get(domain, {})
        common_causes = domain_info.get('common_causes', [])
        
        # Find variables that might be confounders
        potential_confounders = []
        
        for var in available_variables:
            if var != treatment and var != outcome:
                var_lower = var.lower()
                
                # Check if variable matches known confounders
                for common_cause in common_causes:
                    if common_cause in var_lower or var_lower in common_cause:
                        potential_confounders.append(var)
                        break
        
        return potential_confounders
    
    def interpret_causal_relationship(self, cause: str, effect: str, 
                                    effect_size: float, p_value: float, 
                                    domain: str = None) -> str:
        """Generate interpretation of discovered causal relationship."""
        
        # Determine strength
        if effect_size >= 0.5:
            strength = "strong"
        elif effect_size >= 0.3:
            strength = "moderate"
        elif effect_size >= 0.1:
            strength = "weak"
        else:
            strength = "very weak"
        
        # Determine statistical significance
        if p_value < 0.001:
            significance = "highly significant"
        elif p_value < 0.01:
            significance = "significant"
        elif p_value < 0.05:
            significance = "marginally significant"
        else:
            significance = "not statistically significant"
        
        # Generate interpretation
        interpretation = f"The relationship from {cause} to {effect} shows {strength} evidence "
        interpretation += f"(effect size = {effect_size:.3f}) and is {significance} (p = {p_value:.4f}). "
        
        # Add domain-specific insights
        if domain and domain in self.domain_knowledge:
            domain_info = self.domain_knowledge[domain]
            known_relationships = domain_info.get('known_relationships', [])
            
            for known_cause, known_effect in known_relationships:
                if (known_cause.lower() in cause.lower() and known_effect.lower() in effect.lower()) or \
                   (known_cause.lower() in effect.lower() and known_effect.lower() in cause.lower()):
                    interpretation += f"This aligns with established {domain} knowledge that {known_cause} influences {known_effect}. "
                    break
        
        return interpretation

class EnhancedCausalDiscovery:
    """
    Enhanced causal discovery engine combining statistical methods with LLM insights.
    """
    
    def __init__(self, llm_client=None, significance_level: float = 0.05):
        self.statistical_engine = StatisticalCausalDiscovery(significance_level)
        self.llm_assistant = LLMCausalAssistant(llm_client)
        self.significance_level = significance_level
    
    def discover_causal_structure(self, data: pd.DataFrame, 
                                 variables: List[str] = None,
                                 domain: str = None,
                                 max_conditioning_set_size: int = 2) -> CausalDiscoveryResult:
        """
        Discover causal structure in data using hybrid statistical-LLM approach.
        """
        
        if variables is None:
            variables = list(data.columns)
        
        # Auto-detect domain if not provided
        if domain is None:
            domain = self.llm_assistant.detect_domain(variables)
        
        print(f"🔍 Detected domain: {domain}")
        print(f"📊 Analyzing causal relationships among {len(variables)} variables...")
        
        # Step 1: Statistical causal discovery
        statistical_edges = self.statistical_engine.pc_algorithm_simple(data, variables)
        
        # Step 2: Create detailed causal edges with interpretations
        discovered_edges = []
        for cause, effect in statistical_edges:
            # Calculate statistics
            _, p_value = self.statistical_engine.conditional_independence_test(data, cause, effect)
            effect_size = self.statistical_engine.calculate_effect_size(data, cause, effect)
            
            # Determine confidence level
            if effect_size >= 0.3 and p_value < 0.01:
                confidence = 0.9
            elif effect_size >= 0.2 and p_value < 0.05:
                confidence = 0.7
            else:
                confidence = 0.5
            
            # Generate interpretation
            interpretation = self.llm_assistant.interpret_causal_relationship(
                cause, effect, effect_size, p_value, domain
            )
            
            edge = CausalEdge(
                cause=cause,
                effect=effect,
                confidence=confidence,
                method="PC Algorithm + Domain Knowledge",
                p_value=p_value,
                effect_size=effect_size,
                interpretation=interpretation
            )
            
            discovered_edges.append(edge)
        
        # Step 3: Suggest confounders for each causal relationship
        suggested_confounders = {}
        for edge in discovered_edges:
            confounders = self.llm_assistant.suggest_confounders(
                edge.cause, edge.effect, variables, domain
            )
            if confounders:
                suggested_confounders[f"{edge.cause} -> {edge.effect}"] = confounders
        
        # Step 4: Check assumptions
        assumptions_violated = self._check_causal_assumptions(data, discovered_edges)
        
        # Step 5: Generate domain insights
        domain_insights = self._generate_domain_insights(discovered_edges, domain)
        
        # Step 6: Statistical summary
        statistical_summary = {
            'total_relationships_tested': len(list(permutations(variables, 2))),
            'significant_relationships_found': len(discovered_edges),
            'average_effect_size': np.mean([edge.effect_size for edge in discovered_edges]) if discovered_edges else 0,
            'high_confidence_relationships': len([edge for edge in discovered_edges if edge.confidence >= 0.8]),
            'domain': domain
        }
        
        return CausalDiscoveryResult(
            discovered_edges=discovered_edges,
            suggested_confounders=suggested_confounders,
            assumptions_violated=assumptions_violated,
            domain_insights=domain_insights,
            statistical_summary=statistical_summary
        )
    
    def _check_causal_assumptions(self, data: pd.DataFrame, 
                                 edges: List[CausalEdge]) -> List[str]:
        """Check common causal inference assumptions."""
        violations = []
        
        # Check for potential issues
        n_samples = len(data)
        if n_samples < 100:
            violations.append(f"Small sample size (n={n_samples}). Results may be unreliable.")
        
        # Check for missing data
        missing_pct = data.isnull().sum().max() / len(data) * 100
        if missing_pct > 10:
            violations.append(f"High missing data ({missing_pct:.1f}%). May bias causal estimates.")
        
        # Check for potential measurement error
        for edge in edges:
            if edge.effect_size > 0.95:
                violations.append(f"Unusually high effect size for {edge.cause} -> {edge.effect}. "
                                "Check for measurement error or perfect correlation.")
        
        return violations
    
    def _generate_domain_insights(self, edges: List[CausalEdge], domain: str) -> str:
        """Generate domain-specific insights from discovered relationships."""
        
        if not edges:
            return f"No significant causal relationships discovered in {domain} domain."
        
        insights = f"## {domain.title()} Domain Insights\n\n"
        
        # High confidence relationships
        high_conf_edges = [edge for edge in edges if edge.confidence >= 0.8]
        if high_conf_edges:
            insights += f"**Strong Causal Evidence ({len(high_conf_edges)} relationships):**\n"
            for edge in high_conf_edges[:3]:  # Top 3
                insights += f"- {edge.cause} → {edge.effect} (confidence: {edge.confidence:.2f})\n"
            insights += "\n"
        
        # Domain-specific recommendations
        if domain == 'healthcare':
            insights += "**Clinical Recommendations:**\n"
            insights += "- Consider randomized controlled trials to validate causal relationships\n"
            insights += "- Account for patient heterogeneity in treatment effects\n"
            insights += "- Monitor for confounding by indication\n"
        elif domain == 'marketing':
            insights += "**Marketing Strategy Recommendations:**\n"
            insights += "- Test causal relationships through A/B experiments\n"
            insights += "- Consider customer segmentation for personalized interventions\n"
            insights += "- Monitor for seasonality and external market factors\n"
        elif domain == 'finance':
            insights += "**Financial Analysis Recommendations:**\n"
            insights += "- Consider market regime changes and structural breaks\n"
            insights += "- Account for time-varying relationships\n"
            insights += "- Validate with out-of-sample testing\n"
        
        return insights