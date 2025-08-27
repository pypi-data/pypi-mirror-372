#!/usr/bin/env python3
"""
Quick Enhanced CausalLLM Demo

A simple demonstration of the key enhanced features without requiring
complex data generation or long runtime.

Run: python examples/quick_enhanced_demo.py
"""

import sys
import os
import pandas as pd
import numpy as np
import warnings

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

warnings.filterwarnings('ignore')

# Import enhanced CausalLLM components directly
from causallm.core.enhanced_causal_discovery import EnhancedCausalDiscovery
from causallm.core.statistical_inference import StatisticalCausalInference

def create_simple_dataset():
    """Create a simple synthetic dataset for quick testing."""
    np.random.seed(42)
    n = 500
    
    # Simple causal chain: X → M → Y
    X = np.random.normal(0, 1, n)  # Treatment
    M = 2 * X + np.random.normal(0, 0.5, n)  # Mediator
    Y = 1.5 * M + 0.5 * X + np.random.normal(0, 0.3, n)  # Outcome
    
    # Add some confounders
    age = np.random.uniform(25, 65, n)
    Z = 0.1 * age + np.random.normal(0, 1, n)  # Confounder
    
    # Create DataFrame
    data = pd.DataFrame({
        'treatment': X,
        'mediator': M,
        'outcome': Y,
        'age': age,
        'confounder': Z
    })
    
    return data

def quick_demo():
    """Run a quick demonstration of enhanced capabilities."""
    
    print("🚀 Quick Enhanced CausalLLM Demo")
    print("="*40)
    print()
    
    # Create simple data
    print("📊 Creating synthetic dataset...")
    data = create_simple_dataset()
    print(f"   Dataset: {len(data)} samples, {len(data.columns)} variables")
    print(f"   Variables: {list(data.columns)}")
    print()
    
    # 1. Causal Discovery
    print("🔍 Running Causal Discovery...")
    discovery_engine = EnhancedCausalDiscovery()
    
    discovery_results = discovery_engine.discover_causal_structure(
        data, 
        variables=['treatment', 'mediator', 'outcome', 'age']
    )
    
    print("   Discovered relationships:")
    for edge in discovery_results.discovered_edges:
        print(f"   • {edge.cause} → {edge.effect} (confidence: {edge.confidence:.3f})")
    print()
    
    # 2. Statistical Inference
    print("📈 Running Statistical Causal Inference...")
    inference_engine = StatisticalCausalInference()
    
    # Test treatment → outcome
    inference_result = inference_engine.comprehensive_causal_analysis(
        data=data,
        treatment='treatment',
        outcome='outcome',
        covariates=['age']
    )
    
    effect = inference_result.primary_effect
    print(f"   Treatment Effect: {effect.effect_estimate:.4f}")
    print(f"   95% CI: [{effect.confidence_interval[0]:.4f}, {effect.confidence_interval[1]:.4f}]")
    print(f"   P-value: {effect.p_value:.6f}")
    print(f"   Confidence: {inference_result.confidence_level}")
    print()
    
    # 3. Show Value
    print("💡 Key Capabilities Demonstrated:")
    print("   ✅ Automated causal structure discovery")
    print("   ✅ Statistical effect estimation with confidence intervals")
    print("   ✅ Multiple method validation")
    print("   ✅ Domain knowledge integration")
    print("   ✅ Actionable quantitative results")
    print()
    
    print("🎯 This replaces manual:")
    print("   • DAG specification")
    print("   • Method selection")
    print("   • Statistical testing")
    print("   • Result interpretation")
    print("   • Assumption checking")
    print()
    
    print("✨ Enhanced CausalLLM provides scientific rigor")
    print("   with dramatically reduced manual effort!")

if __name__ == "__main__":
    quick_demo()