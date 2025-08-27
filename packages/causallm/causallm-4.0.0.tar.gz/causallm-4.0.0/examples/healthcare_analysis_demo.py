#!/usr/bin/env python3
"""
Healthcare Analysis Demo with Simulated OpenAI Responses

This example demonstrates comprehensive healthcare analysis with realistic
simulated OpenAI responses for clinical decision support without requiring
actual API credentials.

Run: python examples/healthcare_analysis_demo.py
"""

import sys
import os
import json
from datetime import datetime
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from causallm.core.causal_llm_core import CausalLLMCore

class MockOpenAIClient:
    """Mock OpenAI client that provides realistic healthcare analysis responses."""
    
    def chat(self, prompt, temperature=0.7):
        """Simulate OpenAI chat completion for healthcare analysis."""
        
        if "STUDY OVERVIEW" in prompt and "TREATMENT PERFORMANCE" in prompt:
            return self._generate_clinical_analysis(prompt)
        elif "TREATMENT PROTOCOLS" in prompt:
            return self._generate_treatment_recommendations(prompt)
        else:
            return "Mock response: Healthcare analysis completed successfully."
    
    def _generate_clinical_analysis(self, prompt):
        return """# COMPREHENSIVE CLINICAL OUTCOME ANALYSIS

## Executive Summary
This analysis of 1,500 patients reveals significant opportunities for optimizing healthcare delivery through evidence-based treatment protocols and personalized care strategies. The data demonstrates clear performance differences between treatment modalities and identifies critical success factors for improving patient outcomes.

## 🏆 KEY FINDINGS

### Treatment Effectiveness Analysis

**1. Combination Therapy - Superior Performance**
- **Recovery Rate**: 89.3% (highest among all treatments)
- **Clinical Impact**: 12% improvement over standard care
- **Length of Stay**: 6.2 days (20% reduction)
- **Complication Rate**: 8.4% (acceptable given complexity)
- **Cost-Effectiveness**: $18,500 average (justified by outcomes)

**2. Experimental Treatment - Promising Results**
- **Recovery Rate**: 85.7% (8% improvement over standard)
- **Clinical Impact**: Faster recovery with fewer side effects
- **Length of Stay**: 6.8 days (15% reduction)
- **Complication Rate**: 7.2% (lowest complication rate)
- **Cost-Effectiveness**: $16,200 average (excellent value)

**3. Standard Treatment - Baseline Performance**
- **Recovery Rate**: 78.4% (established baseline)
- **Clinical Impact**: Reliable but limited optimization
- **Length of Stay**: 8.1 days (current standard)
- **Complication Rate**: 11.8% (room for improvement)
- **Cost-Effectiveness**: $14,800 average (lowest cost)

### 📊 Patient Population Analysis

**Severity-Based Outcomes:**

**Mild Cases (30% of patients):**
- Recovery rates: 92-96% across all treatments
- Optimal approach: Standard treatment sufficient
- Cost consideration: Avoid overtreatment
- Length of stay: 4-5 days typical

**Moderate Cases (45% of patients):**
- Recovery rates: 80-88% (treatment-dependent)
- Optimal approach: Experimental treatment shows best value
- Critical group: Highest potential for improvement
- Length of stay: 6-8 days with optimization potential

**Severe Cases (25% of patients):**
- Recovery rates: 65-78% (significant treatment impact)
- Optimal approach: Combination therapy essential
- High-risk group: Requires intensive monitoring
- Length of stay: 8-12 days, complication-dependent

### 🔬 Clinical Risk Stratification

**High-Risk Patient Profile:**
- Age >70 years with 3+ comorbidities
- Severe disease presentation (score >70)
- 40% higher complication risk
- Requires specialized care protocols

**Optimal Patient Profile:**
- Age 50-65 with 0-1 comorbidities
- Moderate disease severity
- Best candidates for experimental treatments
- 95%+ recovery potential with appropriate care

## 💡 EVIDENCE-BASED RECOMMENDATIONS

### Immediate Clinical Actions (Week 1-2)
1. **Risk-Stratified Treatment Protocols**: Implement severity-based treatment selection
2. **High-Risk Patient Identification**: Early screening for comorbidity burden
3. **Combination Therapy Expansion**: Increase capacity for severe cases

### Quality Improvement Initiatives (Month 1-3)
1. **Experimental Treatment Scale-Up**: Train staff on new protocols
2. **Complication Prevention Programs**: Focus on high-risk populations
3. **Length of Stay Optimization**: Target 15% reduction through better care coordination

### Long-term Strategic Improvements (Month 3-6)
1. **Personalized Medicine Implementation**: AI-driven treatment selection
2. **Outcome Prediction Models**: Risk-based resource allocation
3. **Cost-Effective Care Pathways**: Optimize treatment intensity by patient profile

## 📈 PROJECTED OUTCOMES

### Clinical Impact Projections
- **Overall Recovery Rate**: 78% → 87% (+11.5% improvement)
- **Complication Reduction**: 10.2% → 7.8% (-24% decrease)
- **Length of Stay**: 7.2 → 6.1 days (-15% reduction)
- **30-day Readmission**: 15% → 11% (-27% decrease)

### Economic Impact Analysis
- **Cost per Successful Outcome**: $19,200 → $17,800 (-7% improvement)
- **Avoided Complications**: $2.3M annual savings
- **Reduced Length of Stay**: $1.8M annual savings
- **Total Economic Benefit**: $4.1M annually for 1,500 patients

## ⚠️ CLINICAL CONSIDERATIONS

### Patient Safety Priorities
- Combination therapy requires enhanced monitoring
- Experimental treatment needs trained specialists
- High-risk patients need individualized protocols

### Implementation Risks
- Staff training requirements for new protocols
- Initial costs for combination therapy setup
- Transition period monitoring essential

### Quality Metrics for Monitoring
- Treatment-specific recovery rates (monthly)
- Complication rates by risk group (weekly)  
- Length of stay trends (continuous)
- Patient satisfaction scores (quarterly)

## 🎯 SUCCESS INDICATORS

### Primary Clinical Metrics
1. **Recovery Rate >85%** across all severity levels
2. **Complication Rate <8%** with proactive prevention
3. **Length of Stay <6.5 days** average
4. **Readmission Rate <12%** within 30 days

### Secondary Quality Measures
- Patient satisfaction >90%
- Staff confidence in protocols >85%
- Cost per case within budget targets
- Adverse event reporting completeness

This analysis provides a roadmap for transforming healthcare delivery through evidence-based protocols, personalized treatment strategies, and continuous quality improvement."""

    def _generate_treatment_recommendations(self, prompt):
        return """# EVIDENCE-BASED TREATMENT PROTOCOL RECOMMENDATIONS

## 🎯 PERSONALIZED TREATMENT ALGORITHMS

### Algorithm 1: Risk-Stratified Treatment Selection

**LOW RISK PATIENTS** (Age <65, 0-1 comorbidities, Mild severity)
```
Treatment Protocol: STANDARD CARE
- Expected Recovery: 94%
- Target Length of Stay: 4-5 days
- Monitoring Level: Standard
- Cost Target: $12,000-15,000
```

**MODERATE RISK PATIENTS** (Age 65-75, 1-2 comorbidities, Moderate severity)
```
Treatment Protocol: EXPERIMENTAL TREATMENT (First Line)
- Expected Recovery: 87%
- Target Length of Stay: 6-7 days
- Monitoring Level: Enhanced
- Cost Target: $16,000-18,000
```

**HIGH RISK PATIENTS** (Age >75, 2+ comorbidities, Severe disease)
```
Treatment Protocol: COMBINATION THERAPY (Mandatory)
- Expected Recovery: 78%
- Target Length of Stay: 8-10 days
- Monitoring Level: Intensive
- Cost Target: $20,000-25,000
```

### Algorithm 2: Dynamic Treatment Escalation

**Step 1: Initial Assessment** (Within 2 hours)
- Age, comorbidity count, severity score
- Hospital resource availability
- Patient preference consideration

**Step 2: Treatment Assignment** (Within 4 hours)
- Risk algorithm application
- Specialist consultation for high-risk cases
- Treatment protocol initiation

**Step 3: Response Monitoring** (Daily evaluation)
- Recovery progress tracking
- Complication screening
- Treatment modification as needed

## 🏥 RESOURCE ALLOCATION RECOMMENDATIONS

### Staffing Requirements by Treatment Type

**Standard Treatment Units**
- Nurse-to-patient ratio: 1:6
- Physician rounds: Twice daily
- Specialist consultations: As needed
- Capacity: 60% of total beds

**Experimental Treatment Units**
- Nurse-to-patient ratio: 1:4
- Physician rounds: Three times daily
- Specialist consultations: Daily
- Capacity: 25% of total beds

**Combination Therapy Units**
- Nurse-to-patient ratio: 1:3
- Physician rounds: Continuous monitoring
- Specialist consultations: Twice daily
- Capacity: 15% of total beds (intensive care level)

### Equipment and Infrastructure

**Essential Upgrades Required:**
1. Advanced monitoring systems for high-risk patients
2. Specialized treatment delivery equipment
3. Enhanced laboratory capabilities
4. Telemedicine infrastructure for remote monitoring

## 📊 QUALITY METRICS AND MONITORING PROTOCOLS

### Daily Metrics (Automated Collection)
- Recovery progress indicators
- Vital sign stability trends  
- Medication adherence rates
- Early warning scores for complications

### Weekly Quality Reviews
- Treatment protocol adherence rates
- Complication analysis and root cause review
- Length of stay variance analysis
- Patient satisfaction trend monitoring

### Monthly Outcome Assessment
- Recovery rate by treatment type and risk group
- Cost-effectiveness analysis
- Readmission pattern analysis
- Staff competency and confidence surveys

## 💰 COST-CONTAINMENT STRATEGIES

### Immediate Cost Savings (Month 1)
1. **Reduce Unnecessary Testing**: Protocol-driven diagnostics (-$200 per patient)
2. **Optimize Length of Stay**: Early discharge protocols (-$800 per patient)
3. **Prevent Complications**: Proactive monitoring (-$2,400 per avoided complication)

### Medium-term Efficiency Gains (Month 2-6)
1. **Treatment Standardization**: Reduce protocol variation (-$500 per patient)
2. **Staff Training Investment**: Improve efficiency and outcomes
3. **Technology Integration**: Automated monitoring and alerts

### Long-term Optimization (Month 6+)
1. **Predictive Analytics**: Risk-based resource allocation
2. **Outcome-Based Protocols**: Continuous improvement cycles
3. **Population Health Management**: Preventive care integration

## 🎯 IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Weeks 1-4)
- Staff training on new protocols
- Risk assessment tool deployment
- Quality metric baseline establishment
- Initial high-risk patient identification

### Phase 2: Protocol Deployment (Weeks 5-12)
- Gradual rollout by patient risk level
- Real-time monitoring and adjustment
- Weekly performance reviews
- Rapid cycle improvements

### Phase 3: Optimization (Weeks 13-26)
- Full protocol implementation
- Advanced analytics deployment
- Outcome-based protocol refinement
- System-wide quality improvements

### Phase 4: Continuous Improvement (Ongoing)
- Monthly protocol updates based on outcomes
- Quarterly comprehensive reviews
- Annual protocol validation studies
- Integration with broader health system initiatives

## 📋 SUCCESS CRITERIA

### Clinical Excellence Targets
- **Recovery Rate**: >87% overall (by month 6)
- **Complication Rate**: <8% overall (by month 3)  
- **Length of Stay**: <6.5 days average (by month 4)
- **Patient Satisfaction**: >90% (by month 6)

### Operational Excellence Targets
- **Protocol Adherence**: >95% (by month 3)
- **Staff Satisfaction**: >85% with new protocols
- **Cost per Case**: Within 5% of target by risk group
- **Quality Metric Reporting**: 100% completeness

### Financial Performance Targets
- **Cost Reduction**: $3,000 per patient average (by year 1)
- **Complication Avoidance**: 50% reduction in preventable complications
- **Readmission Reduction**: 25% decrease in 30-day readmissions
- **ROI**: 4:1 return on implementation investment

This comprehensive protocol framework provides the structure for delivering personalized, evidence-based care while optimizing clinical outcomes and healthcare costs."""

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
    """Run the healthcare analysis demo."""
    
    print("🏥 " + "="*75)
    print("   COMPREHENSIVE HEALTHCARE ANALYSIS DEMO")
    print("="*78)
    print("   (Simulated OpenAI responses for demonstration)")
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
    
    # Calculate key performance metrics
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
    
    print("📈 HEALTHCARE PERFORMANCE METRICS")
    print("-" * 40)
    print(f"Average Patient Age: {avg_age:.1f} years")
    print(f"Overall Recovery Rate: {overall_recovery_rate:.1f}%")
    print(f"Complication Rate: {overall_complication_rate:.1f}%")
    print(f"30-day Readmission Rate: {overall_readmission_rate:.1f}%")
    print(f"Average Length of Stay: {avg_los:.1f} days")
    print(f"Average Cost per Patient: ${avg_cost:,.0f}")
    print()
    
    print("🏥 TREATMENT PERFORMANCE COMPARISON")
    print("-" * 45)
    for treatment in treatment_stats.index:
        stats = treatment_stats.loc[treatment]
        print(f"{treatment.upper()} TREATMENT:")
        print(f"  • Recovery Rate: {stats['recovery_success']*100:.1f}%")
        print(f"  • Length of Stay: {stats['length_of_stay']:.1f} days")
        print(f"  • Complication Rate: {stats['complications']*100:.1f}%")
        print(f"  • Average Cost: ${stats['total_cost']:,.0f}")
        print(f"  • 30-day Readmission: {stats['readmission_30day']*100:.1f}%")
        print()
    
    print("📊 SEVERITY-BASED OUTCOMES")
    print("-" * 30)
    for severity in severity_stats.index:
        stats = severity_stats.loc[severity]
        print(f"{severity.upper()} CASES:")
        print(f"  • Recovery Rate: {stats['recovery_success']*100:.1f}%")
        print(f"  • Length of Stay: {stats['length_of_stay']:.1f} days")
        print(f"  • Complication Rate: {stats['complications']*100:.1f}%")
        print(f"  • Average Cost: ${stats['total_cost']:,.0f}")
        print()
    
    # Simulate OpenAI analysis
    print("🤖 Running AI-Powered Healthcare Analysis...")
    mock_client = MockOpenAIClient()
    
    print("🎯 AI CLINICAL ANALYSIS RESULTS")
    print("-" * 40)
    
    # Generate analysis prompt (simulated)
    analysis_prompt = f"""
    STUDY OVERVIEW:
    - Total patients analyzed: {total_patients:,}
    - Average patient age: {avg_age:.1f} years
    - Overall recovery rate: {overall_recovery_rate:.1f}%
    - Average length of stay: {avg_los:.1f} days
    - Overall complication rate: {overall_complication_rate:.1f}%

    TREATMENT PERFORMANCE COMPARISON:
    [Treatment statistics included]
    """
    
    clinical_analysis = mock_client.chat(analysis_prompt)
    print(clinical_analysis)
    print()
    
    # Generate treatment recommendations
    print("💊 AI TREATMENT PROTOCOL RECOMMENDATIONS")
    print("-" * 45)
    
    recommendation_prompt = f"""
    TREATMENT PROTOCOLS:
    - Best performing treatment: combination
    - Most cost-effective treatment: experimental
    - Overall recovery rate: {overall_recovery_rate:.1f}%
    - Average cost per patient: ${avg_cost:,.0f}
    - Complication rate: {overall_complication_rate:.1f}%
    """
    
    treatment_recommendations = mock_client.chat(recommendation_prompt + "TREATMENT PROTOCOLS")
    print(treatment_recommendations)
    print()
    
    # Create causal healthcare model
    print("🧠 CAUSAL MODEL ANALYSIS")
    print("-" * 28)
    
    try:
        causal_model = create_causal_healthcare_model(patient_data)
        
        # Scenario 1: Universal experimental treatment
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
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'dataset_summary': {
            'total_patients': total_patients,
            'avg_age': float(avg_age),
            'overall_recovery_rate': float(overall_recovery_rate),
            'overall_complication_rate': float(overall_complication_rate),
            'avg_length_of_stay': float(avg_los),
            'avg_cost': float(avg_cost)
        },
        'treatment_performance': treatment_stats.to_dict(),
        'severity_outcomes': severity_stats.to_dict(),
        'ai_clinical_analysis': clinical_analysis,
        'treatment_recommendations': treatment_recommendations
    }
    
    try:
        with open('healthcare_analysis_demo_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print("💾 Results saved to: healthcare_analysis_demo_results.json")
    except Exception as e:
        print(f"   ⚠️ Could not save results: {e}")
    
    print()
    print("🎯 DEMO COMPLETE - KEY HEALTHCARE INSIGHTS")
    print("-" * 45)
    print("✅ Generated comprehensive 1,500-patient dataset")
    print("✅ Analyzed treatment effectiveness across multiple outcomes")  
    print("✅ Provided AI-powered clinical recommendations")
    print("✅ Demonstrated causal healthcare relationship modeling")
    print("✅ Showed evidence-based protocol optimization")
    print("✅ Calculated cost-effectiveness and quality improvements")
    print()
    print("🔗 To run with actual OpenAI API:")
    print("   1. Set OPENAI_API_KEY environment variable")
    print("   2. Set OPENAI_PROJECT_ID (optional)")
    print("   3. Run: python examples/healthcare_analysis_openai.py")
    print()
    print("📚 For more examples, see: USAGE_EXAMPLES.md")

if __name__ == "__main__":
    main()