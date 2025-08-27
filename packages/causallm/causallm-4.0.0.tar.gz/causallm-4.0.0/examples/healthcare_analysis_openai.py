#!/usr/bin/env python3
"""
Healthcare Analysis with OpenAI Integration

This example demonstrates comprehensive healthcare analysis using CausalLLM
with actual OpenAI API calls for clinical decision support, treatment optimization,
and patient outcome prediction.

Prerequisites:
- Set OPENAI_API_KEY environment variable
- Set OPENAI_PROJECT_ID environment variable (optional)
- Install: pip install openai pandas numpy

Run: python examples/healthcare_analysis_openai.py
"""

import sys
import os
import json
from datetime import datetime, timedelta
import random
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from causallm.core.causal_llm_core import CausalLLMCore
from causallm.core.llm_client import get_llm_client

def generate_comprehensive_patient_data():
    """Generate realistic patient data for healthcare analysis."""
    np.random.seed(42)
    n_patients = 1500
    
    # Patient demographics
    ages = np.random.normal(58, 18, n_patients)
    ages = np.clip(ages, 18, 95)
    
    genders = np.random.choice(['Male', 'Female'], n_patients, p=[0.48, 0.52])
    
    # Comorbidities (influenced by age)
    diabetes_prob = np.clip(0.05 + 0.008 * (ages - 30), 0, 0.4)
    diabetes = np.random.binomial(1, diabetes_prob, n_patients)
    
    hypertension_prob = np.clip(0.1 + 0.012 * (ages - 25), 0, 0.6)
    hypertension = np.random.binomial(1, hypertension_prob, n_patients)
    
    heart_disease_prob = np.clip(0.02 + 0.006 * (ages - 40), 0, 0.3)
    heart_disease = np.random.binomial(1, heart_disease_prob, n_patients)
    
    # Calculate comorbidity count
    comorbidity_count = diabetes + hypertension + heart_disease
    
    # Disease severity (influenced by age and comorbidities)
    severity_base = 20 + 0.8 * (ages - 30) + 15 * comorbidity_count
    severity_scores = severity_base + np.random.normal(0, 12, n_patients)
    severity_scores = np.clip(severity_scores, 0, 100)
    
    severity_categories = pd.cut(severity_scores, 
                                bins=[0, 30, 60, 100], 
                                labels=['mild', 'moderate', 'severe'])
    
    # Hospital factors
    hospital_types = np.random.choice(['academic', 'community', 'specialized'], 
                                     n_patients, p=[0.3, 0.5, 0.2])
    
    # Treatment assignment (influenced by severity and hospital type)
    treatments = []
    for i in range(n_patients):
        severity = severity_categories[i]
        hospital = hospital_types[i]
        
        # Base probabilities by severity
        if severity == 'severe':
            base_probs = [0.2, 0.3, 0.5]  # More aggressive for severe cases
        elif severity == 'moderate':
            base_probs = [0.4, 0.4, 0.2]  # Balanced for moderate
        else:  # mild
            base_probs = [0.6, 0.3, 0.1]  # Conservative for mild
        
        # Adjust by hospital type
        if hospital == 'academic':
            # Academic hospitals more likely to use experimental
            probs = [base_probs[0] * 0.7, base_probs[1] * 1.2, base_probs[2] * 1.1]
        elif hospital == 'specialized':
            # Specialized centers prefer combination
            probs = [base_probs[0] * 0.8, base_probs[1] * 0.9, base_probs[2] * 1.3]
        else:  # community
            # Community hospitals prefer standard
            probs = [base_probs[0] * 1.2, base_probs[1] * 0.9, base_probs[2] * 0.8]
        
        # Normalize probabilities
        probs = np.array(probs)
        probs = probs / probs.sum()
        
        treatments.append(np.random.choice(['standard', 'experimental', 'combination'], p=probs))
    
    # Clinical outcomes
    # Length of stay (influenced by age, severity, comorbidities, treatment)
    base_los = 3 + 0.08 * (ages - 30) + 0.15 * severity_scores + 2 * comorbidity_count
    
    treatment_los_effect = np.where(
        np.array(treatments) == 'experimental', -0.8,
        np.where(np.array(treatments) == 'combination', -1.2, 0)
    )
    
    length_of_stay = base_los + treatment_los_effect + np.random.normal(0, 1.5, n_patients)
    length_of_stay = np.clip(length_of_stay, 1, 30)
    
    # Recovery success (influenced by all factors)
    recovery_base_prob = 0.85 - 0.003 * (ages - 40) - 0.008 * severity_scores - 0.05 * comorbidity_count
    
    treatment_recovery_effect = np.where(
        np.array(treatments) == 'experimental', 0.08,
        np.where(np.array(treatments) == 'combination', 0.12, 0)
    )
    
    recovery_prob = recovery_base_prob + treatment_recovery_effect
    recovery_prob = np.clip(recovery_prob, 0.3, 0.98)
    
    recovery_success = np.random.binomial(1, recovery_prob, n_patients)
    
    # Complications (influenced by age, severity, comorbidities)
    complication_base_prob = 0.08 + 0.002 * (ages - 40) + 0.003 * severity_scores + 0.03 * comorbidity_count
    
    treatment_complication_effect = np.where(
        np.array(treatments) == 'experimental', -0.02,
        np.where(np.array(treatments) == 'combination', 0.01, 0)
    )
    
    complication_prob = complication_base_prob + treatment_complication_effect
    complication_prob = np.clip(complication_prob, 0.01, 0.4)
    
    complications = np.random.binomial(1, complication_prob, n_patients)
    
    # Healthcare costs (influenced by all factors)
    base_cost = 5000 + 100 * (ages - 30) + 80 * severity_scores + 2000 * comorbidity_count
    base_cost += 500 * length_of_stay + 8000 * complications
    
    treatment_cost_effect = np.where(
        np.array(treatments) == 'experimental', 3000,
        np.where(np.array(treatments) == 'combination', 5000, 0)
    )
    
    total_costs = base_cost + treatment_cost_effect + np.random.normal(0, 1000, n_patients)
    total_costs = np.clip(total_costs, 2000, 50000)
    
    # 30-day readmission
    readmission_base_prob = 0.12 + 0.001 * (ages - 40) + 0.002 * severity_scores + 0.04 * comorbidity_count
    readmission_base_prob += 0.15 * complications + 0.05 * (1 - recovery_success)
    
    treatment_readmission_effect = np.where(
        np.array(treatments) == 'experimental', -0.03,
        np.where(np.array(treatments) == 'combination', -0.05, 0)
    )
    
    readmission_prob = readmission_base_prob + treatment_readmission_effect
    readmission_prob = np.clip(readmission_prob, 0.02, 0.4)
    
    readmissions = np.random.binomial(1, readmission_prob, n_patients)
    
    return pd.DataFrame({
        'patient_id': range(1, n_patients + 1),
        'age': ages.round(0),
        'gender': genders,
        'diabetes': diabetes,
        'hypertension': hypertension,
        'heart_disease': heart_disease,
        'comorbidity_count': comorbidity_count,
        'severity_score': severity_scores.round(1),
        'severity_category': severity_categories.astype(str),
        'hospital_type': hospital_types,
        'treatment': treatments,
        'length_of_stay': length_of_stay.round(1),
        'recovery_success': recovery_success,
        'complications': complications,
        'total_cost': total_costs.round(0),
        'readmission_30day': readmissions
    })

def analyze_clinical_outcomes_with_openai(patient_data):
    """Perform clinical outcome analysis using OpenAI."""
    
    print("🤖 Initializing OpenAI client for healthcare analysis...")
    
    try:
        # Create OpenAI client
        openai_client = get_llm_client("openai", "gpt-4")
        print("   ✅ OpenAI client initialized successfully")
    except Exception as e:
        print(f"   ❌ Failed to initialize OpenAI client: {e}")
        return None
    
    # Calculate key metrics
    total_patients = len(patient_data)
    avg_age = patient_data['age'].mean()
    avg_los = patient_data['length_of_stay'].mean()
    overall_recovery_rate = patient_data['recovery_success'].mean() * 100
    overall_complication_rate = patient_data['complications'].mean() * 100
    overall_readmission_rate = patient_data['readmission_30day'].mean() * 100
    avg_cost = patient_data['total_cost'].mean()
    
    # Treatment-specific metrics
    treatment_stats = patient_data.groupby('treatment').agg({
        'length_of_stay': 'mean',
        'recovery_success': 'mean',
        'complications': 'mean',
        'total_cost': 'mean',
        'readmission_30day': 'mean'
    }).round(3)
    
    # Severity-specific metrics  
    severity_stats = patient_data.groupby('severity_category').agg({
        'length_of_stay': 'mean',
        'recovery_success': 'mean',
        'complications': 'mean',
        'total_cost': 'mean'
    }).round(3)
    
    # Create comprehensive analysis prompt
    analysis_prompt = f"""
    As a senior clinical data scientist and healthcare analyst, analyze this comprehensive patient outcome data:

    STUDY OVERVIEW:
    - Total patients analyzed: {total_patients:,}
    - Average patient age: {avg_age:.1f} years
    - Average length of stay: {avg_los:.1f} days
    - Overall recovery rate: {overall_recovery_rate:.1f}%
    - Overall complication rate: {overall_complication_rate:.1f}%
    - 30-day readmission rate: {overall_readmission_rate:.1f}%
    - Average treatment cost: ${avg_cost:,.0f}

    TREATMENT PERFORMANCE COMPARISON:
    """
    
    for treatment in ['standard', 'experimental', 'combination']:
        if treatment in treatment_stats.index:
            stats = treatment_stats.loc[treatment]
            los = stats['length_of_stay']
            recovery = stats['recovery_success'] * 100
            complications = stats['complications'] * 100
            cost = stats['total_cost']
            readmission = stats['readmission_30day'] * 100
            
            analysis_prompt += f"""
    {treatment.upper()} TREATMENT:
    - Average length of stay: {los:.1f} days
    - Recovery rate: {recovery:.1f}%
    - Complication rate: {complications:.1f}%
    - Average cost: ${cost:,.0f}
    - 30-day readmission rate: {readmission:.1f}%
    """
    
    analysis_prompt += f"""
    
    SEVERITY-BASED OUTCOMES:
    """
    
    for severity in ['mild', 'moderate', 'severe']:
        if severity in severity_stats.index:
            stats = severity_stats.loc[severity]
            los = stats['length_of_stay']
            recovery = stats['recovery_success'] * 100
            complications = stats['complications'] * 100
            cost = stats['total_cost']
            
            analysis_prompt += f"""
    {severity.upper()} CASES:
    - Average length of stay: {los:.1f} days
    - Recovery rate: {recovery:.1f}%
    - Complication rate: {complications:.1f}%
    - Average cost: ${cost:,.0f}
    """
    
    analysis_prompt += """

    ANALYSIS REQUIREMENTS:
    1. Identify the most effective treatment approach for different patient populations
    2. Analyze cost-effectiveness and clinical outcomes by treatment type
    3. Provide evidence-based recommendations for treatment protocols
    4. Identify high-risk patient groups requiring special attention
    5. Suggest quality improvement initiatives based on the data
    6. Calculate potential cost savings and outcome improvements
    7. Recommend personalized treatment strategies based on patient characteristics

    Please provide a comprehensive clinical analysis with specific, actionable recommendations for improving patient outcomes and healthcare efficiency.
    """
    
    print("📊 Running comprehensive healthcare analysis with OpenAI...")
    
    try:
        clinical_analysis = openai_client.chat(
            prompt=analysis_prompt,
            temperature=0.2  # Lower temperature for clinical analysis
        )
        
        print("   ✅ Clinical analysis completed successfully")
        return {
            'analysis': clinical_analysis,
            'summary_metrics': {
                'total_patients': total_patients,
                'avg_age': avg_age,
                'avg_los': avg_los,
                'overall_recovery_rate': overall_recovery_rate,
                'overall_complication_rate': overall_complication_rate,
                'overall_readmission_rate': overall_readmission_rate,
                'avg_cost': avg_cost
            },
            'treatment_performance': treatment_stats.to_dict(),
            'severity_outcomes': severity_stats.to_dict()
        }
        
    except Exception as e:
        print(f"   ❌ Clinical analysis failed: {e}")
        return None

def generate_treatment_recommendations(analysis_results, patient_data, openai_client):
    """Generate personalized treatment recommendations using OpenAI."""
    
    if not analysis_results:
        return None
    
    # Identify key patterns from the data
    high_risk_factors = patient_data[
        (patient_data['complications'] == 1) | 
        (patient_data['readmission_30day'] == 1) | 
        (patient_data['recovery_success'] == 0)
    ]['comorbidity_count'].describe()
    
    best_performing_treatment = patient_data.groupby('treatment')['recovery_success'].mean().idxmax()
    most_cost_effective = patient_data.groupby('treatment').apply(
        lambda x: x['recovery_success'].mean() / (x['total_cost'].mean() / 1000)
    ).idxmax()
    
    recommendation_prompt = f"""
    Based on this comprehensive healthcare analysis, create detailed, evidence-based treatment protocols:

    CURRENT PERFORMANCE SUMMARY:
    - Best performing treatment: {best_performing_treatment}
    - Most cost-effective treatment: {most_cost_effective}
    - Overall recovery rate: {analysis_results['summary_metrics']['overall_recovery_rate']:.1f}%
    - Average cost per patient: ${analysis_results['summary_metrics']['avg_cost']:,.0f}
    - Complication rate: {analysis_results['summary_metrics']['overall_complication_rate']:.1f}%

    HIGH-RISK PATIENT CHARACTERISTICS:
    - Patients with complications/readmissions have average {high_risk_factors['mean']:.1f} comorbidities
    - Age and comorbidity burden strongly correlate with poor outcomes

    REQUIREMENTS FOR TREATMENT PROTOCOLS:
    1. Personalized treatment algorithms based on patient risk factors
    2. Specific criteria for treatment selection (age, severity, comorbidities)
    3. Resource allocation recommendations for different patient populations
    4. Quality metrics and monitoring protocols
    5. Cost-containment strategies without compromising outcomes
    6. Prevention strategies for high-risk complications
    7. Optimal length of stay guidelines by treatment type

    Please provide detailed, implementable treatment protocols with clear decision trees and measurable outcomes.
    """
    
    try:
        treatment_recommendations = openai_client.chat(
            prompt=recommendation_prompt,
            temperature=0.1  # Very low temperature for medical recommendations
        )
        
        return treatment_recommendations
        
    except Exception as e:
        print(f"   ❌ Treatment recommendation generation failed: {e}")
        return None

def create_causal_healthcare_model(patient_data):
    """Create causal model for healthcare outcomes."""
    
    # Define healthcare context
    healthcare_context = """
    In a comprehensive healthcare system, patient outcomes depend on multiple 
    interconnected factors including patient demographics, comorbidities, disease severity,
    hospital characteristics, and treatment approaches. Age influences disease severity 
    and complication risk. Comorbidities increase complexity and resource requirements.
    Treatment selection affects recovery rates, length of stay, and costs.
    Hospital type influences available resources and treatment protocols.
    Complications significantly impact patient outcomes and healthcare costs.
    """
    
    # Calculate average values for variables
    avg_age = patient_data['age'].mean()
    avg_severity = patient_data['severity_score'].mean()
    avg_comorbidities = patient_data['comorbidity_count'].mean()
    recovery_rate = patient_data['recovery_success'].mean() * 100
    complication_rate = patient_data['complications'].mean() * 100
    avg_cost = patient_data['total_cost'].mean()
    avg_los = patient_data['length_of_stay'].mean()
    
    # Define current healthcare state
    healthcare_variables = {
        "patient_age": f"{avg_age:.0f} years average patient age",
        "disease_severity": f"{avg_severity:.1f} average severity score",
        "comorbidity_burden": f"{avg_comorbidities:.1f} average comorbidities per patient",
        "treatment_protocol": "mixed treatment approaches (40% standard, 33% experimental, 27% combination)",
        "hospital_resources": "varied hospital types (30% academic, 50% community, 20% specialized)",
        "recovery_outcomes": f"{recovery_rate:.1f}% overall recovery rate",
        "complication_rates": f"{complication_rate:.1f}% complication rate",
        "length_of_stay": f"{avg_los:.1f} days average length of stay",
        "healthcare_costs": f"${avg_cost:,.0f} average cost per patient",
        "quality_metrics": "comprehensive outcome tracking across all domains"
    }
    
    # Define causal relationships in healthcare
    healthcare_dag = [
        ('patient_age', 'disease_severity'),
        ('patient_age', 'comorbidity_burden'),
        ('patient_age', 'complication_rates'),
        ('disease_severity', 'treatment_protocol'),
        ('disease_severity', 'length_of_stay'),
        ('comorbidity_burden', 'treatment_protocol'),
        ('comorbidity_burden', 'complication_rates'),
        ('treatment_protocol', 'recovery_outcomes'),
        ('treatment_protocol', 'complication_rates'),
        ('treatment_protocol', 'healthcare_costs'),
        ('hospital_resources', 'treatment_protocol'),
        ('hospital_resources', 'quality_metrics'),
        ('recovery_outcomes', 'length_of_stay'),
        ('recovery_outcomes', 'healthcare_costs'),
        ('complication_rates', 'length_of_stay'),
        ('complication_rates', 'healthcare_costs'),
        ('length_of_stay', 'healthcare_costs'),
        ('quality_metrics', 'recovery_outcomes')
    ]
    
    return CausalLLMCore(healthcare_context, healthcare_variables, healthcare_dag)

def main():
    """Run the comprehensive healthcare analysis with OpenAI integration."""
    
    print("🏥 " + "="*75)
    print("   COMPREHENSIVE HEALTHCARE ANALYSIS WITH OPENAI INTEGRATION")
    print("="*78)
    print()
    
    # Generate comprehensive patient data
    print("📊 Generating comprehensive patient dataset...")
    patient_data = generate_comprehensive_patient_data()
    
    print(f"   ✅ Generated data for {len(patient_data):,} patients")
    print(f"   ✅ Age range: {patient_data['age'].min():.0f}-{patient_data['age'].max():.0f} years")
    print(f"   ✅ Treatment distribution: {patient_data['treatment'].value_counts().to_dict()}")
    print(f"   ✅ Overall recovery rate: {patient_data['recovery_success'].mean()*100:.1f}%")
    print(f"   ✅ Total healthcare costs: ${patient_data['total_cost'].sum():,.0f}")
    print()
    
    # Analyze clinical outcomes with OpenAI
    analysis_results = analyze_clinical_outcomes_with_openai(patient_data)
    
    if analysis_results:
        print("🎯 AI CLINICAL ANALYSIS RESULTS")
        print("-" * 40)
        print(analysis_results['analysis'])
        print()
        
        # Generate treatment recommendations
        print("💊 GENERATING TREATMENT RECOMMENDATIONS")
        print("-" * 45)
        
        try:
            openai_client = get_llm_client("openai", "gpt-4")
            treatment_recommendations = generate_treatment_recommendations(
                analysis_results, patient_data, openai_client
            )
            
            if treatment_recommendations:
                print("🎯 AI TREATMENT PROTOCOL RECOMMENDATIONS")
                print("-" * 45)
                print(treatment_recommendations)
                print()
        except Exception as e:
            print(f"   ❌ Could not generate treatment recommendations: {e}")
        
        # Create causal healthcare model
        print("🧠 CAUSAL MODEL ANALYSIS")
        print("-" * 28)
        
        try:
            causal_model = create_causal_healthcare_model(patient_data)
            
            # Scenario 1: Implement experimental treatment as standard
            print("🧪 SCENARIO 1: Universal Experimental Treatment")
            print("-" * 48)
            experimental_scenario = causal_model.simulate_do({
                "treatment_protocol": "experimental treatment as standard protocol for eligible patients"
            })
            print(experimental_scenario)
            print()
            
            # Scenario 2: Enhanced hospital resources
            print("🏥 SCENARIO 2: Enhanced Hospital Resources")
            print("-" * 42)
            resource_scenario = causal_model.simulate_do({
                "hospital_resources": "upgraded to specialized care capabilities across facilities",
                "quality_metrics": "implemented comprehensive quality monitoring systems"
            })
            print(resource_scenario)
            print()
            
            # Scenario 3: Personalized treatment protocols
            print("👤 SCENARIO 3: AI-Driven Personalized Treatment")
            print("-" * 47)
            personalized_scenario = causal_model.simulate_do({
                "treatment_protocol": "AI-guided personalized treatment selection based on patient risk profile",
                "disease_severity": "early intervention strategies for severe cases",
                "complication_rates": "proactive complication prevention protocols"
            })
            print(personalized_scenario)
            print()
            
        except Exception as e:
            print(f"   ❌ Causal model analysis failed: {e}")
        
        # Save comprehensive results
        save_healthcare_results(patient_data, analysis_results)
        
    else:
        print("❌ Healthcare analysis failed. Check your OpenAI API configuration.")
        return
    
    print("🎯 HEALTHCARE ANALYSIS COMPLETE")
    print("-" * 35)
    print("✅ Generated comprehensive patient dataset with realistic outcomes")
    print("✅ Performed AI-powered clinical outcome analysis")
    print("✅ Created evidence-based treatment recommendations")
    print("✅ Analyzed causal relationships in healthcare delivery")
    print("✅ Demonstrated cost-effectiveness and quality improvement opportunities")
    print()
    print("📁 Results saved to: healthcare_analysis_results.json")
    print("📚 For more examples, see: USAGE_EXAMPLES.md")

def save_healthcare_results(patient_data, analysis_results):
    """Save comprehensive healthcare analysis results."""
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'dataset_summary': {
            'total_patients': len(patient_data),
            'age_statistics': {
                'mean': float(patient_data['age'].mean()),
                'min': float(patient_data['age'].min()),
                'max': float(patient_data['age'].max()),
                'std': float(patient_data['age'].std())
            },
            'treatment_distribution': patient_data['treatment'].value_counts().to_dict(),
            'severity_distribution': patient_data['severity_category'].value_counts().to_dict(),
            'overall_outcomes': {
                'recovery_rate': float(patient_data['recovery_success'].mean()),
                'complication_rate': float(patient_data['complications'].mean()),
                'readmission_rate': float(patient_data['readmission_30day'].mean()),
                'avg_length_of_stay': float(patient_data['length_of_stay'].mean()),
                'avg_cost': float(patient_data['total_cost'].mean())
            },
            'sample_patients': patient_data.head(10).to_dict('records')
        },
        'ai_clinical_analysis': analysis_results['analysis'] if analysis_results else None,
        'summary_metrics': analysis_results['summary_metrics'] if analysis_results else None,
        'treatment_performance': analysis_results['treatment_performance'] if analysis_results else None,
        'severity_outcomes': analysis_results['severity_outcomes'] if analysis_results else None
    }
    
    try:
        with open('healthcare_analysis_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"   ✅ Comprehensive results saved to healthcare_analysis_results.json")
    except Exception as e:
        print(f"   ⚠️  Could not save results: {e}")

if __name__ == "__main__":
    main()