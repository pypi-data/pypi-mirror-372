# CausalLLM Examples

This directory contains practical examples demonstrating how to use CausalLLM for causal inference and analysis across different domains.

## Quick Start

Run any example directly:

```bash
# Healthcare treatment analysis
python examples/healthcare_analysis.py

# Marketing campaign attribution  
python examples/marketing_attribution.py
```

## Examples Overview

### 🏥 Healthcare Analysis
**File**: `healthcare_analysis.py`

**Demonstrates**:
- Treatment effectiveness analysis
- Patient outcome prediction
- Clinical decision support
- Causal intervention modeling

**Key Features**:
- Realistic patient data generation
- Treatment protocol optimization
- Complication risk assessment
- Recovery time prediction

### 📈 Marketing Attribution
**File**: `marketing_attribution.py`

**Demonstrates**:
- Multi-channel campaign attribution
- Budget allocation optimization
- Channel interaction analysis
- Customer lifetime value modeling

**Key Features**:
- Campaign ROI simulation
- Cross-channel synergy analysis
- Personalization impact assessment
- Attribution prompt generation

## Usage Pattern

Each example follows this structure:

1. **Context Definition**: Define the domain-specific scenario
2. **Variable Setup**: Specify current state of key variables  
3. **DAG Construction**: Map causal relationships
4. **Scenario Analysis**: Simulate interventions
5. **Insight Generation**: Create reasoning prompts
6. **Results Interpretation**: Analyze outcomes

## Core CausalLLM Features Demonstrated

✅ **Causal DAG Modeling**: Structure cause-and-effect relationships  
✅ **Do-Calculus Simulation**: Test "what-if" intervention scenarios  
✅ **Reasoning Prompt Generation**: Create structured analysis tasks  
✅ **Domain Knowledge Integration**: Combine expertise with statistical inference  
✅ **Decision Support**: Generate actionable insights for optimization

## Extending the Examples

To adapt these examples to your domain:

1. **Define Your Context**: Describe your business/research scenario
2. **Identify Variables**: List key factors and their current states  
3. **Map Relationships**: Determine causal dependencies
4. **Test Interventions**: Simulate changes and analyze impact
5. **Generate Insights**: Create prompts for deeper analysis

## Next Steps

- See `USAGE_EXAMPLES.md` for more comprehensive use cases
- Check the main `README.md` for installation and setup
- Explore the `tests/` directory for additional code examples
- Visit the documentation for API reference

## Requirements

- Python 3.8+
- CausalLLM library
- NumPy, Pandas (for data examples)

No LLM API keys required for basic functionality!