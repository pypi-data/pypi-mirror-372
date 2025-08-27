#!/usr/bin/env python3
"""
Healthcare Treatment Analysis Example

This example demonstrates how to use CausalLLM to analyze treatment effectiveness
and generate causal insights for healthcare decision-making.

Run: python examples/healthcare_analysis.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from causallm.core.causal_llm_core import CausalLLMCore

def generate_sample_data():
    """Generate realistic healthcare data for demonstration."""
    np.random.seed(42)
    n_patients = 1000
    
    # Generate correlated healthcare data
    age = np.random.normal(65, 15, n_patients)
    age = np.clip(age, 18, 95)  # Realistic age range
    
    # Severity correlates with age
    severity_score = 0.3 * (age - 40) + np.random.normal(0, 10, n_patients)
    severity_score = np.clip(severity_score, 0, 100)
    severity = pd.cut(severity_score, bins=[0, 30, 70, 100], labels=['mild', 'moderate', 'severe'])
    
    # Treatment assignment (somewhat influenced by severity)
    treatment = np.random.choice(['standard', 'experimental', 'combination'], n_patients, p=[0.4, 0.3, 0.3])
    
    # Recovery days (influenced by age, severity, treatment)
    base_recovery = 10 + 0.1 * age + 0.3 * severity_score
    treatment_effect = np.where(treatment == 'experimental', -2, 
                               np.where(treatment == 'combination', -3, 0))
    recovery_days = base_recovery + treatment_effect + np.random.normal(0, 3, n_patients)
    recovery_days = np.clip(recovery_days, 3, 60)
    
    # Complications (influenced by age and treatment)
    complication_prob = 0.1 + 0.005 * (age - 40) + 0.001 * severity_score
    treatment_complication_effect = np.where(treatment == 'experimental', -0.05,
                                            np.where(treatment == 'combination', 0.02, 0))
    complication_prob += treatment_complication_effect
    complications = np.random.binomial(1, np.clip(complication_prob, 0, 1), n_patients)
    
    return pd.DataFrame({
        'age': age,
        'severity': severity.astype(str),
        'treatment': treatment,
        'recovery_days': recovery_days,
        'complications': complications
    })

def main():
    """Run healthcare causal analysis example."""
    print("🏥 " + "="*60)
    print("   CAUSALLM HEALTHCARE ANALYSIS EXAMPLE")
    print("="*63)
    print()
    
    # Generate sample data
    print("📊 Generating sample healthcare data...")
    data = generate_sample_data()
    print(f"   Generated data for {len(data)} patients")
    print(f"   Average age: {data['age'].mean():.1f} years")
    print(f"   Severity distribution: {data['severity'].value_counts().to_dict()}")
    print(f"   Treatment distribution: {data['treatment'].value_counts().to_dict()}")
    print()
    
    # Define causal context
    context = """
    In a clinical study, patients with varying ages and disease severity receive different treatments.
    Older patients typically have more severe conditions and longer recovery times.
    Treatment type significantly affects recovery time and complication rates.
    The experimental treatment shows promise for faster recovery but needs validation.
    Combination therapy may reduce recovery time but might increase complexity.
    """
    
    # Define variables and their baseline states
    variables = {
        "age": "65 years average",
        "severity": "moderate severity predominant",
        "treatment": "standard treatment protocol",
        "recovery_days": "15 days average recovery",
        "complications": "12% complication rate"
    }
    
    # Define causal relationships (DAG)
    dag_edges = [
        ('age', 'severity'),            # Age influences disease severity
        ('age', 'recovery_days'),       # Age affects recovery time
        ('age', 'complications'),       # Age affects complication risk
        ('severity', 'treatment'),      # Severity influences treatment choice
        ('severity', 'recovery_days'),  # Severity affects recovery time
        ('severity', 'complications'),  # Severity affects complication risk
        ('treatment', 'recovery_days'), # Treatment affects recovery time
        ('treatment', 'complications'), # Treatment affects complications
    ]
    
    print("🧠 Setting up causal reasoning model...")
    try:
        # Create causal reasoning core
        core = CausalLLMCore(context, variables, dag_edges)
        print("   ✅ Causal model initialized successfully")
        print(f"   ✅ DAG created with {len(dag_edges)} causal relationships")
        print()
        
        # Analysis 1: What if we switch to experimental treatment?
        print("🧪 ANALYSIS 1: Experimental Treatment Impact")
        print("-" * 50)
        experimental_result = core.simulate_do({"treatment": "experimental treatment"})
        print(experimental_result)
        print()
        
        # Analysis 2: What if we use combination therapy for severe cases?
        print("🔬 ANALYSIS 2: Combination Therapy for Severe Cases")
        print("-" * 55)
        combination_result = core.simulate_do({
            "treatment": "combination therapy",
            "severity": "severe cases prioritized"
        })
        print(combination_result)
        print()
        
        # Analysis 3: Generate clinical reasoning prompt
        print("💡 ANALYSIS 3: Clinical Decision Support")
        print("-" * 45)
        reasoning_task = "recommend optimal treatment protocol based on patient age and severity"
        reasoning_prompt = core.generate_reasoning_prompt(reasoning_task)
        print("Generated clinical reasoning prompt:")
        print(reasoning_prompt)
        print()
        
        # Statistical summary of actual data
        print("📈 DATA INSIGHTS FROM SAMPLE")
        print("-" * 35)
        print(f"Recovery time by treatment:")
        recovery_by_treatment = data.groupby('treatment')['recovery_days'].agg(['mean', 'std']).round(1)
        for treatment, stats in recovery_by_treatment.iterrows():
            print(f"  {treatment:>12}: {stats['mean']:5.1f} ± {stats['std']:4.1f} days")
        
        print(f"\nComplication rate by treatment:")
        complication_by_treatment = data.groupby('treatment')['complications'].mean() * 100
        for treatment, rate in complication_by_treatment.items():
            print(f"  {treatment:>12}: {rate:5.1f}%")
        
        print(f"\nRecovery time by severity:")
        recovery_by_severity = data.groupby('severity')['recovery_days'].mean()
        for severity, avg_time in recovery_by_severity.items():
            print(f"  {severity:>12}: {avg_time:5.1f} days")
            
        print()
        
    except Exception as e:
        print(f"   ❌ Error in causal analysis: {e}")
        return
    
    print("🎯 KEY TAKEAWAYS")
    print("-" * 20)
    print("✅ CausalLLM successfully modeled healthcare causal relationships")
    print("✅ Generated intervention scenarios for treatment optimization")
    print("✅ Created structured reasoning prompts for clinical decisions")
    print("✅ Combined domain knowledge with statistical insights")
    print()
    print("💡 Next Steps:")
    print("   • Integrate with real patient data")
    print("   • Add LLM provider for enhanced reasoning")
    print("   • Implement A/B testing framework")
    print("   • Develop clinical decision dashboards")
    print()
    print("📚 For more examples, see: USAGE_EXAMPLES.md")

if __name__ == "__main__":
    main()