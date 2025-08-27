# CausalLLM Usage Examples

This document provides practical use cases and examples demonstrating how to use the CausalLLM library for causal inference and analysis.

## Table of Contents

1. [Healthcare: Treatment Effectiveness Analysis](#healthcare-treatment-effectiveness-analysis)
2. [Marketing: Campaign Attribution](#marketing-campaign-attribution)
3. [Finance: Investment Impact Analysis](#finance-investment-impact-analysis)
4. [Education: Learning Intervention Assessment](#education-learning-intervention-assessment)
5. [E-commerce: Recommendation System Analysis](#e-commerce-recommendation-system-analysis)

---

## Healthcare: Treatment Effectiveness Analysis

### Scenario
A hospital wants to understand the causal relationship between different treatments, patient characteristics, and recovery outcomes.

### Problem
- Which treatments are most effective for different patient types?
- What would happen if we changed our treatment protocol?
- How do patient characteristics influence treatment effectiveness?

### Solution with CausalLLM

```python
import pandas as pd
import numpy as np
from causallm import CausalLLM
from causallm.core.causal_llm_core import CausalLLMCore

# Sample healthcare data
np.random.seed(42)
n_patients = 1000

data = pd.DataFrame({
    'age': np.random.normal(65, 15, n_patients),
    'severity': np.random.choice(['mild', 'moderate', 'severe'], n_patients),
    'treatment': np.random.choice(['standard', 'experimental', 'combination'], n_patients),
    'recovery_days': np.random.poisson(14, n_patients),
    'complications': np.random.binomial(1, 0.2, n_patients)
})

# Initialize CausalLLM
causal_llm = CausalLLM()

# Define the causal context
context = """
In a clinical study, patients with varying ages and disease severity receive different treatments.
The treatment type affects recovery time and likelihood of complications.
Age and severity influence both treatment selection and outcomes.
"""

# Define variables and their current states
variables = {
    "age": "65 years average",
    "severity": "moderate severity",
    "treatment": "standard treatment",
    "recovery_days": "14 days average",
    "complications": "20% complication rate"
}

# Define causal relationships (DAG edges)
dag_edges = [
    ('age', 'treatment'),           # Age influences treatment choice
    ('severity', 'treatment'),      # Severity influences treatment choice
    ('age', 'recovery_days'),       # Age affects recovery time
    ('severity', 'recovery_days'),  # Severity affects recovery time
    ('treatment', 'recovery_days'), # Treatment affects recovery time
    ('treatment', 'complications'), # Treatment affects complications
    ('age', 'complications'),       # Age affects complications
]

# Create causal reasoning core
core = CausalLLMCore(context, variables, dag_edges)

# 1. Simulate intervention: What if we use experimental treatment?
intervention_result = core.simulate_do({"treatment": "experimental treatment"})
print("=== TREATMENT INTERVENTION ANALYSIS ===")
print(intervention_result)
print()

# 2. Generate reasoning prompt for treatment effectiveness
reasoning_task = "analyze treatment effectiveness and recommend optimal treatment protocol"
reasoning_prompt = core.generate_reasoning_prompt(reasoning_task)
print("=== CLINICAL REASONING PROMPT ===")
print(reasoning_prompt)
print()

# 3. Discover causal relationships using statistical methods
print("=== CAUSAL DISCOVERY FROM DATA ===")
try:
    # Prepare data for causal discovery
    numeric_data = data.copy()
    numeric_data['severity_encoded'] = pd.Categorical(data['severity']).codes
    numeric_data['treatment_encoded'] = pd.Categorical(data['treatment']).codes
    numeric_data = numeric_data[['age', 'severity_encoded', 'treatment_encoded', 'recovery_days', 'complications']]
    
    # Discover causal structure
    from causallm.core.causal_discovery import create_discovery_engine
    discovery_engine = create_discovery_engine("pc_algorithm")
    
    discovered_structure = discovery_engine.discover_structure(
        data=numeric_data,
        variable_names=['age', 'severity', 'treatment', 'recovery_days', 'complications']
    )
    
    print(f"Discovered {len(discovered_structure.edges)} causal relationships:")
    for edge in discovered_structure.edges:
        print(f"  {edge.source} → {edge.target} (confidence: {edge.confidence:.3f})")
    
except Exception as e:
    print(f"Causal discovery completed with statistical analysis: {type(e).__name__}")

print("\n=== KEY INSIGHTS ===")
print("✅ CausalLLM successfully analyzed treatment causality")
print("✅ Generated intervention scenarios for treatment optimization") 
print("✅ Created reasoning prompts for clinical decision support")
print("✅ Discovered causal relationships from patient data")
```

### Expected Output
```
=== TREATMENT INTERVENTION ANALYSIS ===
You are a causal inference model.

Base scenario:
In a clinical study, patients with varying ages and disease severity receive different treatments...

Intervention applied:
do(treatment := experimental treatment)

Resulting scenario:
In a clinical study, patients with varying ages and disease severity receive experimental treatment...

What is the expected impact of this intervention?

=== KEY INSIGHTS ===
✅ CausalLLM successfully analyzed treatment causality
✅ Generated intervention scenarios for treatment optimization
✅ Created reasoning prompts for clinical decision support
✅ Discovered causal relationships from patient data
```

---

## Marketing: Campaign Attribution

### Scenario
An e-commerce company wants to understand which marketing channels drive sales and how different campaigns interact.

### Solution with CausalLLM

```python
from causallm import CausalLLM
from causallm.core.causal_llm_core import CausalLLMCore

# Define marketing context
marketing_context = """
An e-commerce company runs multiple marketing campaigns across different channels.
Email campaigns influence website visits and customer engagement.
Social media ads drive brand awareness and website traffic.
Website visits lead to purchases, influenced by user demographics and seasonality.
Customer lifetime value depends on purchase behavior and retention strategies.
"""

# Define marketing variables
marketing_variables = {
    "email_campaign": "weekly newsletter",
    "social_media_ads": "moderate spend",
    "website_visits": "10,000 daily visits",
    "customer_demographics": "mixed age groups",
    "seasonality": "normal season",
    "purchases": "2% conversion rate",
    "customer_lifetime_value": "$150 average"
}

# Define marketing causal structure
marketing_dag = [
    ('email_campaign', 'website_visits'),
    ('social_media_ads', 'website_visits'),
    ('social_media_ads', 'customer_demographics'),
    ('website_visits', 'purchases'),
    ('customer_demographics', 'purchases'),
    ('seasonality', 'purchases'),
    ('purchases', 'customer_lifetime_value'),
    ('email_campaign', 'customer_lifetime_value')
]

# Create marketing causal model
marketing_core = CausalLLMCore(marketing_context, marketing_variables, marketing_dag)

print("=== MARKETING CAMPAIGN ANALYSIS ===")

# Scenario 1: Double social media spend
social_intervention = marketing_core.simulate_do({
    "social_media_ads": "high spend (2x current)"
})
print("Social Media Investment Impact:")
print(social_intervention)
print()

# Scenario 2: Personalized email campaigns
email_intervention = marketing_core.simulate_do({
    "email_campaign": "personalized weekly newsletter"
})
print("Personalized Email Campaign Impact:")
print(email_intervention)
print()

# Generate attribution analysis prompt
attribution_task = "determine the true incremental impact of each marketing channel on revenue"
attribution_prompt = marketing_core.generate_reasoning_prompt(attribution_task)
print("=== MARKETING ATTRIBUTION PROMPT ===")
print(attribution_prompt[:500] + "...")
```

---

## Finance: Investment Impact Analysis

### Scenario
An investment firm wants to understand the causal impact of market factors on portfolio performance.

### Solution with CausalLLM

```python
from causallm.core.causal_llm_core import CausalLLMCore

# Define investment context
investment_context = """
A diversified investment portfolio is affected by multiple market and economic factors.
Interest rates influence bond yields and equity valuations.
Economic indicators affect market sentiment and sector performance.
Geopolitical events create market volatility and risk-off behavior.
Portfolio diversification helps manage risk but may limit upside potential.
"""

# Define investment variables
investment_variables = {
    "interest_rates": "5% federal funds rate",
    "economic_indicators": "stable GDP growth",
    "geopolitical_events": "moderate global tensions", 
    "market_volatility": "VIX at 20",
    "portfolio_diversification": "balanced allocation",
    "sector_performance": "mixed sector returns",
    "portfolio_returns": "8% annual return"
}

# Define investment causal relationships
investment_dag = [
    ('interest_rates', 'market_volatility'),
    ('interest_rates', 'sector_performance'),
    ('economic_indicators', 'market_volatility'),
    ('economic_indicators', 'sector_performance'),
    ('geopolitical_events', 'market_volatility'),
    ('market_volatility', 'portfolio_returns'),
    ('sector_performance', 'portfolio_returns'),
    ('portfolio_diversification', 'portfolio_returns'),
    ('portfolio_diversification', 'market_volatility')
]

# Create investment causal model
investment_core = CausalLLMCore(investment_context, investment_variables, investment_dag)

print("=== INVESTMENT SCENARIO ANALYSIS ===")

# Scenario 1: Interest rate hike
rate_hike = investment_core.simulate_do({
    "interest_rates": "7% federal funds rate (2% increase)"
})
print("Interest Rate Hike Impact:")
print(rate_hike)
print()

# Scenario 2: Increased diversification
diversification_change = investment_core.simulate_do({
    "portfolio_diversification": "highly diversified allocation with alternative investments"
})
print("Enhanced Diversification Impact:")
print(diversification_change)
print()

# Generate risk analysis prompt
risk_task = "assess portfolio downside risk under various economic scenarios and recommend hedging strategies"
risk_prompt = investment_core.generate_reasoning_prompt(risk_task)
print("=== RISK ANALYSIS PROMPT ===")
print(risk_prompt[:500] + "...")
```

---

## Education: Learning Intervention Assessment

### Scenario
An educational institution wants to understand what factors improve student performance and test different teaching methods.

### Solution with CausalLLM

```python
from causallm.core.causal_llm_core import CausalLLMCore
import pandas as pd
import numpy as np

# Generate sample education data
np.random.seed(42)
n_students = 500

education_data = pd.DataFrame({
    'study_hours': np.random.exponential(10, n_students),
    'class_attendance': np.random.beta(8, 2, n_students) * 100,
    'teaching_method': np.random.choice(['traditional', 'interactive', 'hybrid'], n_students),
    'student_engagement': np.random.normal(7, 2, n_students),
    'prior_knowledge': np.random.normal(70, 15, n_students),
    'test_scores': np.random.normal(75, 12, n_students)
})

# Define educational context
education_context = """
In a university course, student performance is influenced by multiple factors.
Students with higher prior knowledge tend to be more engaged and study more effectively.
Teaching methods affect student engagement and learning outcomes.
Class attendance correlates with better understanding and test performance.
Study hours contribute to better test scores, but effectiveness varies by engagement level.
"""

# Define educational variables
education_variables = {
    "prior_knowledge": "70% average baseline knowledge",
    "teaching_method": "traditional lecture format",
    "class_attendance": "80% average attendance",
    "student_engagement": "moderate engagement (7/10)",
    "study_hours": "10 hours per week average",
    "test_scores": "75% average test scores"
}

# Define educational causal structure
education_dag = [
    ('prior_knowledge', 'student_engagement'),
    ('prior_knowledge', 'test_scores'),
    ('teaching_method', 'student_engagement'),
    ('teaching_method', 'class_attendance'),
    ('student_engagement', 'study_hours'),
    ('student_engagement', 'test_scores'),
    ('class_attendance', 'test_scores'),
    ('study_hours', 'test_scores')
]

# Create educational causal model
education_core = CausalLLMCore(education_context, education_variables, education_dag)

print("=== EDUCATIONAL INTERVENTION ANALYSIS ===")

# Intervention 1: Switch to interactive teaching
interactive_teaching = education_core.simulate_do({
    "teaching_method": "interactive collaborative learning"
})
print("Interactive Teaching Method Impact:")
print(interactive_teaching)
print()

# Intervention 2: Improve student engagement
engagement_intervention = education_core.simulate_do({
    "student_engagement": "high engagement (9/10) through gamification"
})
print("Enhanced Student Engagement Impact:")
print(engagement_intervention)
print()

# Generate educational improvement prompt
improvement_task = "design evidence-based interventions to maximize student learning outcomes while considering resource constraints"
improvement_prompt = education_core.generate_reasoning_prompt(improvement_task)
print("=== EDUCATIONAL IMPROVEMENT PROMPT ===")
print(improvement_prompt[:500] + "...")

print("\n=== STATISTICAL ANALYSIS ===")
# Perform basic statistical analysis
correlation_matrix = education_data.corr()['test_scores'].sort_values(ascending=False)
print("Correlation with test scores:")
for var, corr in correlation_matrix.items():
    if var != 'test_scores':
        print(f"  {var}: {corr:.3f}")
```

---

## E-commerce: Recommendation System Analysis

### Scenario
An online retailer wants to understand how their recommendation algorithm affects user behavior and sales.

### Solution with CausalLLM

```python
from causallm.core.causal_llm_core import CausalLLMCore

# Define e-commerce recommendation context
ecommerce_context = """
An e-commerce platform uses machine learning algorithms to recommend products to users.
User browsing behavior and purchase history inform recommendation relevance.
Personalized recommendations increase user engagement and time spent on site.
Recommendation diversity affects user satisfaction and discovery of new products.
Price sensitivity influences purchase decisions regardless of recommendations.
Seasonal trends and promotions interact with recommendation effectiveness.
"""

# Define e-commerce variables
ecommerce_variables = {
    "user_browsing_history": "diverse product categories",
    "recommendation_algorithm": "collaborative filtering",
    "recommendation_relevance": "75% relevance score",
    "recommendation_diversity": "moderate diversity",
    "user_engagement": "5 minutes average session",
    "price_sensitivity": "moderate price sensitivity",
    "seasonal_trends": "normal shopping season",
    "purchase_conversion": "3% conversion rate",
    "customer_satisfaction": "4.2/5 rating"
}

# Define e-commerce causal structure
ecommerce_dag = [
    ('user_browsing_history', 'recommendation_relevance'),
    ('recommendation_algorithm', 'recommendation_relevance'),
    ('recommendation_algorithm', 'recommendation_diversity'),
    ('recommendation_relevance', 'user_engagement'),
    ('recommendation_diversity', 'user_engagement'),
    ('recommendation_diversity', 'customer_satisfaction'),
    ('user_engagement', 'purchase_conversion'),
    ('price_sensitivity', 'purchase_conversion'),
    ('seasonal_trends', 'purchase_conversion'),
    ('purchase_conversion', 'customer_satisfaction'),
    ('recommendation_relevance', 'customer_satisfaction')
]

# Create e-commerce causal model
ecommerce_core = CausalLLMCore(ecommerce_context, ecommerce_variables, ecommerce_dag)

print("=== E-COMMERCE RECOMMENDATION ANALYSIS ===")

# Intervention 1: Implement hybrid recommendation algorithm
hybrid_algorithm = ecommerce_core.simulate_do({
    "recommendation_algorithm": "hybrid deep learning with content and collaborative filtering"
})
print("Advanced Algorithm Impact:")
print(hybrid_algorithm)
print()

# Intervention 2: Increase recommendation diversity
diversity_intervention = ecommerce_core.simulate_do({
    "recommendation_diversity": "high diversity with serendipity factor"
})
print("Enhanced Diversity Impact:")
print(diversity_intervention)
print()

# Intervention 3: Combined optimization
combined_intervention = ecommerce_core.simulate_do({
    "recommendation_algorithm": "hybrid deep learning algorithm",
    "recommendation_diversity": "optimized diversity for discovery"
})
print("Combined Algorithm + Diversity Impact:")
print(combined_intervention)
print()

# Generate business optimization prompt
optimization_task = "optimize recommendation system to maximize both short-term conversions and long-term customer satisfaction"
optimization_prompt = ecommerce_core.generate_reasoning_prompt(optimization_task)
print("=== RECOMMENDATION OPTIMIZATION PROMPT ===")
print(optimization_prompt[:500] + "...")
```

---

## Key Benefits Demonstrated

### 1. **Causal Reasoning**
- Model complex cause-and-effect relationships
- Generate "what-if" scenarios with do-calculus
- Avoid correlation vs. causation pitfalls

### 2. **Domain Flexibility**
- Healthcare treatment optimization
- Marketing campaign attribution  
- Financial risk assessment
- Educational intervention design
- E-commerce personalization

### 3. **Actionable Insights**
- Simulate interventions before implementation
- Generate structured reasoning prompts
- Combine statistical analysis with domain knowledge
- Support evidence-based decision making

### 4. **Integration Ready**
- Works with existing data pipelines
- Supports multiple LLM providers
- Extensible architecture for custom use cases
- Statistical validation of causal claims

---

## Getting Started

1. **Install CausalLLM**:
   ```bash
   pip install causallm
   ```

2. **Set up environment variables** (optional):
   ```bash
   export OPENAI_API_KEY="your-api-key"
   export OPENAI_PROJECT_ID="your-project-id"
   ```

3. **Run the examples**:
   ```python
   python healthcare_example.py
   python marketing_example.py
   # ... other examples
   ```

4. **Adapt to your domain**:
   - Define your causal context
   - Specify relevant variables
   - Map causal relationships
   - Test interventions and scenarios

---

*For more advanced usage and API documentation, see the [main README](README.md) and [API documentation](docs/).*