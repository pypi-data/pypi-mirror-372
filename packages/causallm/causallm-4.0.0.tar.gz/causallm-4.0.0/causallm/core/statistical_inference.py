"""
Statistical Causal Inference Engine

This module provides comprehensive statistical methods for causal effect estimation,
including multiple approaches for robustness and validation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import warnings
from scipy import stats
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import NearestNeighbors

warnings.filterwarnings('ignore')

class CausalMethod(Enum):
    """Available causal inference methods."""
    LINEAR_REGRESSION = "linear_regression"
    MATCHING = "propensity_score_matching" 
    INSTRUMENTAL_VARIABLES = "instrumental_variables"
    REGRESSION_DISCONTINUITY = "regression_discontinuity"
    DIFFERENCE_IN_DIFFERENCES = "difference_in_differences"
    RANDOMIZED_EXPERIMENT = "randomized_experiment"

@dataclass
class CausalEffect:
    """Represents estimated causal effect."""
    treatment: str
    outcome: str
    method: str
    effect_estimate: float
    confidence_interval: Tuple[float, float]
    p_value: float
    standard_error: float
    sample_size: int
    interpretation: str
    assumptions_met: List[str]
    assumptions_violated: List[str]
    robustness_score: float

@dataclass
class CausalInferenceResult:
    """Complete causal inference analysis result."""
    primary_effect: CausalEffect
    robustness_checks: List[CausalEffect]
    sensitivity_analysis: Dict[str, Any]
    recommendations: str
    confidence_level: str
    overall_assessment: str

class PropensityScoreMatching:
    """Propensity score matching for causal inference."""
    
    def __init__(self, caliper: float = 0.1):
        self.caliper = caliper
        self.propensity_model = None
        self.matched_indices = None
    
    def fit_propensity_model(self, X: pd.DataFrame, treatment: pd.Series) -> float:
        """Fit propensity score model and return AUC."""
        try:
            # Use logistic regression for propensity scores
            self.propensity_model = LogisticRegression(random_state=42, max_iter=1000)
            
            # Handle categorical variables
            X_processed = pd.get_dummies(X, drop_first=True)
            
            # Standardize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_processed)
            
            # Fit model
            self.propensity_model.fit(X_scaled, treatment)
            
            # Calculate AUC for model quality
            from sklearn.metrics import roc_auc_score
            y_pred_proba = self.propensity_model.predict_proba(X_scaled)[:, 1]
            auc = roc_auc_score(treatment, y_pred_proba)
            
            return auc
            
        except Exception as e:
            print(f"Warning: Propensity model fitting failed: {e}")
            return 0.5
    
    def match_samples(self, X: pd.DataFrame, treatment: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
        """Perform propensity score matching."""
        try:
            # Get propensity scores
            X_processed = pd.get_dummies(X, drop_first=True)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_processed)
            
            propensity_scores = self.propensity_model.predict_proba(X_scaled)[:, 1]
            
            # Find matches
            treated_indices = np.where(treatment == 1)[0]
            control_indices = np.where(treatment == 0)[0]
            
            matched_treated = []
            matched_control = []
            
            for treated_idx in treated_indices:
                treated_score = propensity_scores[treated_idx]
                
                # Find closest control unit within caliper
                control_scores = propensity_scores[control_indices]
                distances = np.abs(control_scores - treated_score)
                
                closest_control_idx = np.argmin(distances)
                closest_distance = distances[closest_control_idx]
                
                if closest_distance <= self.caliper:
                    matched_treated.append(treated_idx)
                    matched_control.append(control_indices[closest_control_idx])
            
            return np.array(matched_treated), np.array(matched_control)
            
        except Exception as e:
            print(f"Warning: Matching failed: {e}")
            return np.array([]), np.array([])
    
    def estimate_effect(self, outcome_treated: pd.Series, outcome_control: pd.Series) -> Tuple[float, float, float]:
        """Estimate treatment effect from matched samples."""
        if len(outcome_treated) == 0 or len(outcome_control) == 0:
            return 0.0, 0.0, 1.0
        
        # Calculate mean difference
        effect = outcome_treated.mean() - outcome_control.mean()
        
        # Calculate standard error
        var_treated = outcome_treated.var() / len(outcome_treated)
        var_control = outcome_control.var() / len(outcome_control)
        se = np.sqrt(var_treated + var_control)
        
        # T-test
        t_stat = effect / se if se > 0 else 0
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), len(outcome_treated) + len(outcome_control) - 2))
        
        return effect, se, p_value

class InstrumentalVariables:
    """Instrumental variables estimation."""
    
    def __init__(self):
        self.first_stage_model = None
        self.reduced_form_model = None
    
    def check_instrument_strength(self, instrument: pd.Series, treatment: pd.Series, 
                                 covariates: pd.DataFrame = None) -> Dict[str, float]:
        """Check instrument strength using first-stage F-statistic."""
        try:
            # Prepare data
            if covariates is not None:
                X = pd.concat([instrument.to_frame(), covariates], axis=1)
            else:
                X = instrument.to_frame()
            
            X_processed = pd.get_dummies(X, drop_first=True)
            
            # First stage regression
            first_stage = LinearRegression()
            first_stage.fit(X_processed, treatment)
            
            # Calculate F-statistic for instrument
            y_pred = first_stage.predict(X_processed)
            residuals = treatment - y_pred
            
            # F-statistic calculation (simplified)
            mse_residual = np.mean(residuals**2)
            mse_instrument = np.var(y_pred)
            
            f_stat = mse_instrument / mse_residual if mse_residual > 0 else 0
            
            # Rule of thumb: F > 10 for strong instrument
            strength_assessment = "strong" if f_stat > 10 else "weak" if f_stat > 3 else "very_weak"
            
            return {
                'f_statistic': f_stat,
                'strength': strength_assessment,
                'first_stage_r2': first_stage.score(X_processed, treatment)
            }
            
        except Exception as e:
            print(f"Warning: Instrument strength check failed: {e}")
            return {'f_statistic': 0, 'strength': 'unknown', 'first_stage_r2': 0}
    
    def two_stage_least_squares(self, instrument: pd.Series, treatment: pd.Series, 
                               outcome: pd.Series, covariates: pd.DataFrame = None) -> Tuple[float, float, float]:
        """Perform 2SLS estimation."""
        try:
            # Prepare data
            if covariates is not None:
                X_first = pd.concat([instrument.to_frame(), covariates], axis=1)
                X_second = pd.concat([treatment.to_frame(), covariates], axis=1)
            else:
                X_first = instrument.to_frame()
                X_second = treatment.to_frame()
            
            X_first_processed = pd.get_dummies(X_first, drop_first=True)
            
            # First stage: regress treatment on instrument
            first_stage = LinearRegression()
            first_stage.fit(X_first_processed, treatment)
            treatment_fitted = first_stage.predict(X_first_processed)
            
            # Second stage: regress outcome on fitted treatment
            if covariates is not None:
                X_second_processed = pd.get_dummies(X_second, drop_first=True)
                # Replace actual treatment with fitted values
                treatment_col = treatment.name if treatment.name else 'treatment'
                if treatment_col in X_second_processed.columns:
                    X_second_processed[treatment_col] = treatment_fitted
                else:
                    # Add fitted treatment as first column
                    X_second_processed.insert(0, 'treatment_fitted', treatment_fitted)
            else:
                X_second_processed = pd.DataFrame({'treatment_fitted': treatment_fitted})
            
            second_stage = LinearRegression()
            second_stage.fit(X_second_processed, outcome)
            
            # Extract treatment effect (coefficient of treatment)
            effect = second_stage.coef_[0]
            
            # Calculate standard errors (simplified)
            y_pred = second_stage.predict(X_second_processed)
            residuals = outcome - y_pred
            mse = np.mean(residuals**2)
            
            # Approximate standard error
            se = np.sqrt(mse / len(outcome))
            
            # T-test
            t_stat = effect / se if se > 0 else 0
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), len(outcome) - X_second_processed.shape[1]))
            
            return effect, se, p_value
            
        except Exception as e:
            print(f"Warning: 2SLS estimation failed: {e}")
            return 0.0, 0.0, 1.0

class StatisticalCausalInference:
    """
    Comprehensive statistical causal inference engine.
    """
    
    def __init__(self, significance_level: float = 0.05):
        self.significance_level = significance_level
        self.psm = PropensityScoreMatching()
        self.iv = InstrumentalVariables()
    
    def estimate_causal_effect(self, data: pd.DataFrame,
                              treatment: str,
                              outcome: str,
                              covariates: List[str] = None,
                              method: CausalMethod = CausalMethod.LINEAR_REGRESSION,
                              instrument: str = None) -> CausalEffect:
        """
        Estimate causal effect using specified method.
        """
        
        # Prepare data
        treatment_data = data[treatment]
        outcome_data = data[outcome]
        
        if covariates:
            covariate_data = data[covariates]
        else:
            covariate_data = None
        
        # Determine if treatment is binary
        is_binary_treatment = len(treatment_data.unique()) == 2
        
        # Estimate effect based on method
        if method == CausalMethod.LINEAR_REGRESSION:
            effect_est, se, p_val = self._linear_regression_estimate(
                treatment_data, outcome_data, covariate_data
            )
            assumptions_met = ["linearity", "no_perfect_multicollinearity"]
            assumptions_violated = []
            
        elif method == CausalMethod.MATCHING and is_binary_treatment:
            effect_est, se, p_val = self._matching_estimate(
                treatment_data, outcome_data, covariate_data
            )
            assumptions_met = ["conditional_independence_given_covariates"]
            assumptions_violated = []
            
        elif method == CausalMethod.INSTRUMENTAL_VARIABLES and instrument:
            instrument_data = data[instrument]
            effect_est, se, p_val = self._iv_estimate(
                instrument_data, treatment_data, outcome_data, covariate_data
            )
            assumptions_met = ["instrument_relevance", "instrument_exogeneity"]
            assumptions_violated = []
            
        else:
            # Fallback to linear regression
            effect_est, se, p_val = self._linear_regression_estimate(
                treatment_data, outcome_data, covariate_data
            )
            assumptions_met = ["linearity"]
            assumptions_violated = ["method_not_implemented"]
        
        # Calculate confidence interval
        t_critical = stats.t.ppf(1 - self.significance_level/2, len(data) - 2)
        ci_lower = effect_est - t_critical * se
        ci_upper = effect_est + t_critical * se
        
        # Generate interpretation
        interpretation = self._generate_interpretation(
            treatment, outcome, effect_est, p_val, method
        )
        
        # Calculate robustness score
        robustness_score = self._calculate_robustness_score(effect_est, se, p_val)
        
        return CausalEffect(
            treatment=treatment,
            outcome=outcome,
            method=method.value,
            effect_estimate=effect_est,
            confidence_interval=(ci_lower, ci_upper),
            p_value=p_val,
            standard_error=se,
            sample_size=len(data),
            interpretation=interpretation,
            assumptions_met=assumptions_met,
            assumptions_violated=assumptions_violated,
            robustness_score=robustness_score
        )
    
    def _linear_regression_estimate(self, treatment: pd.Series, outcome: pd.Series, 
                                   covariates: pd.DataFrame = None) -> Tuple[float, float, float]:
        """Estimate causal effect using linear regression."""
        try:
            if covariates is not None:
                X = pd.concat([treatment.to_frame(), covariates], axis=1)
            else:
                X = treatment.to_frame()
            
            X_processed = pd.get_dummies(X, drop_first=True)
            
            # Ensure all data is numeric
            X_processed = X_processed.astype(float)
            outcome = outcome.astype(float)
            
            model = LinearRegression()
            model.fit(X_processed, outcome)
            
            # Treatment effect is first coefficient
            effect = model.coef_[0]
            
            # Calculate standard error using simplified approach
            y_pred = model.predict(X_processed)
            residuals = outcome - y_pred
            mse = np.mean(residuals**2)
            
            # Simplified standard error calculation
            n = len(outcome)
            k = X_processed.shape[1]
            
            if n > k:
                # Standard error approximation
                X_array = X_processed.values.astype(float)
                try:
                    # Try to compute proper standard error
                    XtX_inv = np.linalg.inv(X_array.T @ X_array)
                    se = np.sqrt(mse * XtX_inv[0, 0])
                except:
                    # Fallback to simple approximation
                    se = np.sqrt(mse / n)
            else:
                se = np.sqrt(mse / n) if n > 0 else 0.1
            
            # T-test
            t_stat = effect / se if se > 0 else 0
            df = max(1, n - k)
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))
            
            return effect, se, p_value
            
        except Exception as e:
            print(f"Warning: Linear regression estimation failed: {e}")
            return 0.0, 0.1, 1.0
    
    def _matching_estimate(self, treatment: pd.Series, outcome: pd.Series, 
                          covariates: pd.DataFrame = None) -> Tuple[float, float, float]:
        """Estimate causal effect using propensity score matching."""
        try:
            if covariates is None:
                # Cannot do matching without covariates
                return self._linear_regression_estimate(treatment, outcome, None)
            
            # Fit propensity model
            auc = self.psm.fit_propensity_model(covariates, treatment)
            
            if auc < 0.6:
                print("Warning: Poor propensity model performance (AUC < 0.6)")
            
            # Perform matching
            matched_treated_idx, matched_control_idx = self.psm.match_samples(covariates, treatment)
            
            if len(matched_treated_idx) == 0:
                print("Warning: No matches found, falling back to regression")
                return self._linear_regression_estimate(treatment, outcome, covariates)
            
            # Estimate effect on matched samples
            outcome_treated = outcome.iloc[matched_treated_idx]
            outcome_control = outcome.iloc[matched_control_idx]
            
            effect, se, p_val = self.psm.estimate_effect(outcome_treated, outcome_control)
            
            return effect, se, p_val
            
        except Exception as e:
            print(f"Warning: Matching estimation failed: {e}")
            return 0.0, 0.0, 1.0
    
    def _iv_estimate(self, instrument: pd.Series, treatment: pd.Series, 
                    outcome: pd.Series, covariates: pd.DataFrame = None) -> Tuple[float, float, float]:
        """Estimate causal effect using instrumental variables."""
        try:
            # Check instrument strength
            strength_check = self.iv.check_instrument_strength(instrument, treatment, covariates)
            
            if strength_check['f_statistic'] < 3:
                print("Warning: Weak instrument detected (F < 3)")
            
            # Perform 2SLS
            effect, se, p_val = self.iv.two_stage_least_squares(
                instrument, treatment, outcome, covariates
            )
            
            return effect, se, p_val
            
        except Exception as e:
            print(f"Warning: IV estimation failed: {e}")
            return 0.0, 0.0, 1.0
    
    def _generate_interpretation(self, treatment: str, outcome: str, 
                               effect: float, p_value: float, 
                               method: CausalMethod) -> str:
        """Generate human-readable interpretation of causal effect."""
        
        # Determine statistical significance
        if p_value < 0.001:
            significance = "highly significant"
        elif p_value < 0.01:
            significance = "significant"
        elif p_value < 0.05:
            significance = "marginally significant"
        else:
            significance = "not statistically significant"
        
        # Determine effect size
        abs_effect = abs(effect)
        if abs_effect < 0.1:
            magnitude = "small"
        elif abs_effect < 0.5:
            magnitude = "moderate"
        else:
            magnitude = "large"
        
        direction = "increases" if effect > 0 else "decreases"
        
        interpretation = f"Using {method.value.replace('_', ' ')}, we find that {treatment} "
        interpretation += f"{direction} {outcome} by {abs_effect:.3f} units on average. "
        interpretation += f"This effect is {magnitude} in magnitude and {significance} "
        interpretation += f"(p = {p_value:.4f}). "
        
        # Method-specific notes
        if method == CausalMethod.MATCHING:
            interpretation += "This estimate controls for selection bias through propensity score matching."
        elif method == CausalMethod.INSTRUMENTAL_VARIABLES:
            interpretation += "This estimate addresses potential confounding through instrumental variables."
        elif method == CausalMethod.LINEAR_REGRESSION:
            interpretation += "This estimate assumes no unobserved confounding given included covariates."
        
        return interpretation
    
    def _calculate_robustness_score(self, effect: float, se: float, p_value: float) -> float:
        """Calculate a robustness score for the causal estimate."""
        
        # Based on statistical significance and effect size
        significance_score = max(0, 1 - p_value * 20)  # Higher score for lower p-values
        
        # Effect size relative to standard error
        t_stat = abs(effect / se) if se > 0 else 0
        precision_score = min(1, t_stat / 4)  # Higher score for larger t-statistics
        
        # Combined score
        robustness_score = (significance_score + precision_score) / 2
        
        return robustness_score
    
    def comprehensive_causal_analysis(self, data: pd.DataFrame,
                                    treatment: str,
                                    outcome: str,
                                    covariates: List[str] = None,
                                    instrument: str = None) -> CausalInferenceResult:
        """
        Perform comprehensive causal analysis with multiple methods for robustness.
        """
        
        print(f"🧮 Performing comprehensive causal analysis...")
        print(f"   Treatment: {treatment}")
        print(f"   Outcome: {outcome}")
        print(f"   Covariates: {covariates if covariates else 'None'}")
        print(f"   Sample size: {len(data)}")
        
        # Primary analysis (linear regression)
        primary_effect = self.estimate_causal_effect(
            data, treatment, outcome, covariates, CausalMethod.LINEAR_REGRESSION
        )
        
        # Robustness checks
        robustness_checks = []
        
        # Check if binary treatment for matching
        if len(data[treatment].unique()) == 2 and covariates:
            matching_effect = self.estimate_causal_effect(
                data, treatment, outcome, covariates, CausalMethod.MATCHING
            )
            robustness_checks.append(matching_effect)
        
        # Instrumental variables if instrument provided
        if instrument and instrument in data.columns:
            iv_effect = self.estimate_causal_effect(
                data, treatment, outcome, covariates, 
                CausalMethod.INSTRUMENTAL_VARIABLES, instrument
            )
            robustness_checks.append(iv_effect)
        
        # Sensitivity analysis
        sensitivity_analysis = self._sensitivity_analysis(primary_effect, robustness_checks)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(primary_effect, robustness_checks)
        
        # Determine confidence level
        confidence_level = self._assess_confidence_level(primary_effect, robustness_checks)
        
        # Overall assessment
        overall_assessment = self._generate_overall_assessment(
            primary_effect, robustness_checks, confidence_level
        )
        
        return CausalInferenceResult(
            primary_effect=primary_effect,
            robustness_checks=robustness_checks,
            sensitivity_analysis=sensitivity_analysis,
            recommendations=recommendations,
            confidence_level=confidence_level,
            overall_assessment=overall_assessment
        )
    
    def _sensitivity_analysis(self, primary: CausalEffect, 
                            robustness: List[CausalEffect]) -> Dict[str, Any]:
        """Perform sensitivity analysis across different methods."""
        
        all_effects = [primary] + robustness
        effect_estimates = [e.effect_estimate for e in all_effects]
        
        return {
            'effect_range': (min(effect_estimates), max(effect_estimates)),
            'effect_std': np.std(effect_estimates),
            'methods_agreement': len([e for e in all_effects if e.p_value < 0.05]),
            'consistent_direction': len(set(np.sign(effect_estimates))) == 1,
            'average_robustness_score': np.mean([e.robustness_score for e in all_effects])
        }
    
    def _generate_recommendations(self, primary: CausalEffect, 
                                robustness: List[CausalEffect]) -> str:
        """Generate actionable recommendations based on analysis."""
        
        recommendations = "## Recommendations\n\n"
        
        if primary.p_value < 0.05:
            recommendations += f"✅ **Strong evidence for causal effect**: "
            recommendations += f"{primary.treatment} significantly affects {primary.outcome}.\n\n"
            
            recommendations += "**Next Steps:**\n"
            recommendations += "- Consider implementing interventions based on this finding\n"
            recommendations += "- Monitor effect size in practice for validation\n"
            
            if len(robustness) > 0:
                consistent = all(r.p_value < 0.05 for r in robustness)
                if consistent:
                    recommendations += "- Results are robust across multiple methods ✅\n"
                else:
                    recommendations += "- Results vary across methods - proceed with caution ⚠️\n"
        else:
            recommendations += f"⚠️ **Insufficient evidence for causal effect**: "
            recommendations += f"No significant causal relationship detected.\n\n"
            
            recommendations += "**Possible Actions:**\n"
            recommendations += "- Collect more data to increase statistical power\n"
            recommendations += "- Consider alternative treatments or interventions\n"
            recommendations += "- Re-examine causal assumptions and model specification\n"
        
        return recommendations
    
    def _assess_confidence_level(self, primary: CausalEffect, 
                               robustness: List[CausalEffect]) -> str:
        """Assess overall confidence level in causal estimate."""
        
        all_effects = [primary] + robustness
        significant_effects = [e for e in all_effects if e.p_value < 0.05]
        avg_robustness = np.mean([e.robustness_score for e in all_effects])
        
        if len(significant_effects) == len(all_effects) and avg_robustness > 0.7:
            return "High"
        elif len(significant_effects) >= len(all_effects) / 2 and avg_robustness > 0.5:
            return "Medium"
        else:
            return "Low"
    
    def _generate_overall_assessment(self, primary: CausalEffect,
                                   robustness: List[CausalEffect], 
                                   confidence_level: str) -> str:
        """Generate overall assessment of causal analysis."""
        
        assessment = f"## Overall Assessment: {confidence_level} Confidence\n\n"
        
        if confidence_level == "High":
            assessment += "🎯 **Strong causal evidence** with consistent results across multiple methods. "
            assessment += "The estimated effect is statistically significant and appears robust to "
            assessment += "different analytical approaches.\n\n"
        elif confidence_level == "Medium":
            assessment += "📊 **Moderate causal evidence** with some consistency across methods. "
            assessment += "Results suggest a causal relationship but may be sensitive to methodological choices "
            assessment += "or require additional validation.\n\n"
        else:
            assessment += "🔍 **Limited causal evidence** with inconsistent or non-significant results. "
            assessment += "More data or different analytical approaches may be needed to establish "
            assessment += "a clear causal relationship.\n\n"
        
        # Method-specific insights
        if robustness:
            assessment += "**Method Comparison:**\n"
            assessment += f"- Primary method (regression): {primary.effect_estimate:.3f} (p={primary.p_value:.3f})\n"
            for rob in robustness:
                assessment += f"- {rob.method}: {rob.effect_estimate:.3f} (p={rob.p_value:.3f})\n"
        
        return assessment