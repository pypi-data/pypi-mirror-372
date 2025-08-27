#!/usr/bin/env python3
"""
Marketing Attribution Analysis Demo with Simulated OpenAI Responses

This example demonstrates marketing attribution analysis with realistic
simulated OpenAI responses to show the complete workflow without requiring
actual API credentials.

Run: python examples/marketing_attribution_demo.py
"""

import sys
import os
import json
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from causallm.core.causal_llm_core import CausalLLMCore

class MockOpenAIClient:
    """Mock OpenAI client that provides realistic attribution analysis responses."""
    
    def chat(self, prompt, temperature=0.7):
        """Simulate OpenAI chat completion for marketing attribution analysis."""
        
        if "CHANNEL PERFORMANCE BREAKDOWN" in prompt:
            return self._generate_attribution_analysis(prompt)
        elif "OPTIMIZATION REQUIREMENTS" in prompt:
            return self._generate_optimization_recommendations(prompt)
        else:
            return "Mock response: Analysis completed successfully."
    
    def _generate_attribution_analysis(self, prompt):
        return """# MARKETING ATTRIBUTION ANALYSIS

## Executive Summary
Based on the comprehensive data analysis, your marketing campaigns show strong performance with strategic optimization opportunities. The overall ROAS demonstrates healthy returns, but channel allocation can be significantly improved.

## Channel Performance Analysis

### 🏆 TOP PERFORMING CHANNELS

**1. Search Advertising**
- **Strength**: Highest conversion influence with 4.2x ROAS
- **Insight**: Captures customers at high-intent moments
- **Customer Journey Role**: Primary conversion driver
- **Recommendation**: Increase budget allocation by 25-30%

**2. Email Marketing** 
- **Strength**: Exceptional cost efficiency at $0.12 average CPA
- **Insight**: Strong repeat customer engagement and retention
- **Customer Journey Role**: Relationship nurturing and conversion support
- **Recommendation**: Expand personalization and segmentation strategies

### 📈 GROWTH OPPORTUNITIES

**3. Social Media Advertising**
- **Current Performance**: 2.1x ROAS, strong reach metrics
- **Insight**: Excellent brand awareness driver but lower direct conversions
- **Synergy Effect**: 40% higher conversion rate when combined with email
- **Recommendation**: Focus on retargeting and lookalike audiences

**4. Display Advertising**
- **Current Performance**: 1.8x ROAS, supporting role
- **Insight**: Provides crucial top-of-funnel awareness
- **Attribution Impact**: Increases email and search effectiveness by 15%
- **Recommendation**: Optimize creative messaging and audience targeting

## Cross-Channel Attribution Insights

### 🔗 Channel Synergies Discovered
- **Multi-touch journeys** convert 40% better than single-channel
- **Email + Search combination** shows 3.5x higher lifetime value
- **Social Media** amplifies other channels by improving brand recognition
- **Display advertising** creates 18% lift in search brand queries

### 📊 Customer Journey Patterns
- **Average journey length**: 3.2 touchpoints per conversion
- **Optimal journey**: Social Media → Email → Search → Conversion
- **High-value customers**: Engage with 4+ touchpoints before converting
- **Quick converters**: Direct from search, typically lower AOV

## Revenue Impact Analysis
- **Total Revenue Generated**: $25,691.92
- **Most Valuable Journeys**: Multi-channel sequences (avg $247 AOV)
- **Incremental Revenue Opportunity**: $8,200-12,300 with optimization
- **Channel Attribution**: Email (35%), Search (30%), Social (20%), Display (15%)"""

    def _generate_optimization_recommendations(self, prompt):
        return """# MARKETING OPTIMIZATION PLAN

## 🎯 STRATEGIC RECOMMENDATIONS

### Immediate Actions (Week 1-2)
1. **Reallocate Search Budget**: Increase by $2,500/month (+30%)
2. **Email Segmentation**: Implement behavioral triggers (expected +25% engagement)
3. **Social Media Retargeting**: Launch custom audiences (expected +40% conversion rate)

### Short-term Optimizations (Month 1-2)
1. **Cross-channel Attribution Setup**: Implement unified tracking
2. **Creative Testing**: A/B test display ad messaging alignment
3. **Search Keyword Expansion**: Target high-intent long-tail keywords

### Long-term Strategy (Month 3-6)
1. **Customer Lifetime Value Optimization**: Focus on high-LTV segments
2. **Advanced Attribution Modeling**: Implement time-decay attribution
3. **Channel Integration**: Develop unified customer experience

## 💰 BUDGET REALLOCATION STRATEGY

### Current Allocation Analysis
- Search: $8,200/month → Increase to $10,700/month (+$2,500)
- Email: $1,800/month → Increase to $2,300/month (+$500)
- Social Media: $7,500/month → Maintain at $7,500/month
- Display: $4,200/month → Reduce to $3,500/month (-$700)

### Expected ROI Impact
- **Incremental Revenue**: +$12,500-18,000/month
- **Improved ROAS**: 2.8x → 3.4x overall
- **Cost Efficiency**: 15% reduction in customer acquisition cost
- **Conversion Rate**: +22% improvement expected

## 📊 KEY PERFORMANCE INDICATORS

### Primary KPIs to Track
1. **Revenue Attribution by Channel** (monthly)
2. **Customer Acquisition Cost by Source** (weekly)
3. **Multi-touch Conversion Rates** (bi-weekly)
4. **Customer Lifetime Value by Journey Type** (quarterly)

### Secondary KPIs
- Cross-channel engagement rates
- Time between touchpoints
- Brand search lift from display campaigns
- Email engagement correlation with other channels

## ⚠️ RISK ASSESSMENT

### Low Risk
- Email budget increase (proven high ROAS)
- Search budget optimization (clear performance data)

### Medium Risk  
- Display budget reduction (may impact brand awareness)
- Social media strategy changes (longer measurement cycle)

### Mitigation Strategies
- Gradual budget shifts over 60 days
- Weekly performance monitoring
- A/B test all major changes
- Maintain brand awareness measurement

## 🚀 IMPLEMENTATION TIMELINE

**Week 1**: Search budget increase, email segmentation setup
**Week 2**: Social media retargeting launch  
**Week 3-4**: Display creative testing, keyword expansion
**Month 2**: Attribution system implementation
**Month 3**: Full optimization strategy evaluation

## Expected Outcomes
- **30-day projection**: +$8,500 incremental revenue
- **90-day projection**: +$28,000 incremental revenue  
- **ROI on optimization efforts**: 4.2x return on investment
- **Payback period**: 18 days for implementation costs"""

def generate_marketing_data():
    """Generate realistic marketing attribution data."""
    
    # Customer touchpoints and conversions over 90 days
    touchpoints = []
    conversions = []
    
    # Generate customer journey data
    for customer_id in range(1, 501):  # 500 customers
        journey_start = datetime.now() - timedelta(days=random.randint(1, 90))
        
        # Customer demographics influence channel preferences
        age_group = random.choice(['18-25', '26-35', '36-45', '46-55', '55+'])
        location = random.choice(['urban', 'suburban', 'rural'])
        
        # Generate touchpoints for this customer
        num_touchpoints = random.randint(1, 8)
        customer_touchpoints = []
        
        for i in range(num_touchpoints):
            touch_time = journey_start + timedelta(days=random.randint(0, 30))
            
            # Channel probabilities based on demographics
            if age_group in ['18-25', '26-35']:
                channel = random.choices(
                    ['social_media', 'email', 'search', 'display', 'direct', 'referral'],
                    weights=[0.35, 0.20, 0.20, 0.10, 0.10, 0.05]
                )[0]
            else:
                channel = random.choices(
                    ['email', 'search', 'social_media', 'display', 'direct', 'referral'],
                    weights=[0.30, 0.25, 0.20, 0.10, 0.10, 0.05]
                )[0]
            
            touchpoint = {
                'customer_id': customer_id,
                'timestamp': touch_time.isoformat(),
                'channel': channel,
                'age_group': age_group,
                'location': location,
                'session_duration': random.uniform(30, 600),  # seconds
                'pages_viewed': random.randint(1, 12),
                'channel_cost': get_channel_cost(channel),
                'attribution_position': i + 1,
                'total_journey_length': num_touchpoints
            }
            
            customer_touchpoints.append(touchpoint)
            touchpoints.append(touchpoint)
        
        # Determine if customer converted
        conversion_probability = calculate_conversion_probability(customer_touchpoints)
        
        if random.random() < conversion_probability:
            conversion_time = customer_touchpoints[-1]['timestamp']
            conversion_value = random.uniform(25, 500)  # Purchase value
            
            conversion = {
                'customer_id': customer_id,
                'conversion_timestamp': conversion_time,
                'conversion_value': conversion_value,
                'age_group': age_group,
                'location': location,
                'journey_length': num_touchpoints,
                'time_to_conversion': (touch_time - journey_start).days,
                'touchpoint_sequence': [tp['channel'] for tp in customer_touchpoints]
            }
            
            conversions.append(conversion)
    
    return touchpoints, conversions

def get_channel_cost(channel):
    """Return typical cost per interaction by channel."""
    costs = {
        'social_media': random.uniform(0.50, 2.00),
        'email': random.uniform(0.05, 0.20),
        'search': random.uniform(1.00, 5.00),
        'display': random.uniform(0.30, 1.50),
        'direct': 0.00,
        'referral': random.uniform(0.10, 0.50)
    }
    return costs.get(channel, 1.00)

def calculate_conversion_probability(touchpoints):
    """Calculate conversion probability based on customer journey."""
    base_prob = 0.02  # 2% base conversion rate
    
    # Factors that increase conversion probability
    journey_length_boost = min(len(touchpoints) * 0.015, 0.08)  # More touchpoints = higher conversion
    
    # Channel mix bonus
    unique_channels = len(set(tp['channel'] for tp in touchpoints))
    channel_diversity_boost = min(unique_channels * 0.01, 0.05)
    
    # Email and search are strong conversion drivers
    email_touches = sum(1 for tp in touchpoints if tp['channel'] == 'email')
    search_touches = sum(1 for tp in touchpoints if tp['channel'] == 'search')
    channel_boost = min((email_touches * 0.02) + (search_touches * 0.025), 0.10)
    
    # High engagement boost
    avg_session_duration = sum(tp['session_duration'] for tp in touchpoints) / len(touchpoints)
    engagement_boost = min((avg_session_duration - 60) * 0.0001, 0.05) if avg_session_duration > 60 else 0
    
    total_prob = base_prob + journey_length_boost + channel_diversity_boost + channel_boost + engagement_boost
    return min(total_prob, 0.35)  # Cap at 35% max conversion rate

def create_causal_attribution_model(touchpoints, conversions):
    """Create causal model for marketing attribution."""
    
    # Define marketing attribution context
    attribution_context = """
    Marketing attribution in e-commerce involves understanding how different 
    marketing channels and touchpoints influence customer behavior and conversions.
    Email marketing drives direct engagement and nurtures existing relationships.
    Social media builds brand awareness and reaches new audiences.
    Search advertising captures high-intent traffic at decision moments.
    Display advertising increases brand visibility across the web.
    Customer demographics and behavior patterns influence channel effectiveness.
    Journey length and touchpoint sequence affect conversion probability.
    """
    
    # Define current attribution state
    attribution_variables = {
        "email_effectiveness": "20% of touchpoints, strong conversion influence",
        "social_media_reach": "35% of touchpoints, brand awareness driver",
        "search_intent": "20% of touchpoints, high conversion rate",
        "display_visibility": "15% of touchpoints, supporting awareness",
        "customer_journey_length": "average 3.2 touchpoints per conversion",
        "channel_synergy": "multi-channel journeys show 40% higher conversion",
        "cost_efficiency": f"overall ROAS {sum(c['conversion_value'] for c in conversions) / sum(tp['channel_cost'] for tp in touchpoints):.2f}x",
        "customer_lifetime_value": "average $125 per converted customer"
    }
    
    # Define causal relationships in marketing attribution
    attribution_dag = [
        ('email_effectiveness', 'customer_journey_length'),
        ('email_effectiveness', 'channel_synergy'),
        ('social_media_reach', 'display_visibility'),
        ('social_media_reach', 'customer_journey_length'),
        ('search_intent', 'cost_efficiency'),
        ('search_intent', 'customer_lifetime_value'),
        ('display_visibility', 'channel_synergy'),
        ('customer_journey_length', 'channel_synergy'),
        ('channel_synergy', 'cost_efficiency'),
        ('channel_synergy', 'customer_lifetime_value'),
        ('cost_efficiency', 'customer_lifetime_value')
    ]
    
    return CausalLLMCore(attribution_context, attribution_variables, attribution_dag)

def main():
    """Run the marketing attribution analysis demo."""
    
    print("🎯 " + "="*70)
    print("   MARKETING ATTRIBUTION ANALYSIS DEMO")
    print("="*73)
    print("   (Simulated OpenAI responses for demonstration)")
    print()
    
    # Generate realistic marketing data
    print("📊 Generating marketing attribution dataset...")
    touchpoints, conversions = generate_marketing_data()
    
    print(f"   ✅ Generated {len(touchpoints):,} touchpoints")
    print(f"   ✅ Generated {len(conversions):,} conversions")
    print(f"   ✅ Total revenue: ${sum(c['conversion_value'] for c in conversions):,.2f}")
    print()
    
    # Calculate performance metrics
    total_revenue = sum(c['conversion_value'] for c in conversions)
    total_cost = sum(tp['channel_cost'] for tp in touchpoints)
    overall_roas = total_revenue / total_cost
    conversion_rate = len(conversions) / len(touchpoints) * 100
    
    # Channel performance analysis
    channel_stats = {}
    for tp in touchpoints:
        channel = tp['channel']
        if channel not in channel_stats:
            channel_stats[channel] = {
                'touchpoints': 0,
                'cost': 0,
                'contributing_conversions': 0,
                'revenue_attributed': 0
            }
        channel_stats[channel]['touchpoints'] += 1
        channel_stats[channel]['cost'] += tp['channel_cost']
    
    # Attribution analysis for conversions
    for conversion in conversions:
        customer_journey = conversion['touchpoint_sequence']
        revenue_per_touchpoint = conversion['conversion_value'] / len(customer_journey)
        
        for channel in customer_journey:
            if channel in channel_stats:
                channel_stats[channel]['contributing_conversions'] += 1
                channel_stats[channel]['revenue_attributed'] += revenue_per_touchpoint
    
    print("📈 PERFORMANCE METRICS SUMMARY")
    print("-" * 40)
    print(f"Overall ROAS: {overall_roas:.2f}x")
    print(f"Conversion Rate: {conversion_rate:.2f}%")
    print(f"Total Revenue: ${total_revenue:,.2f}")
    print(f"Total Cost: ${total_cost:,.2f}")
    print()
    
    print("📊 CHANNEL PERFORMANCE BREAKDOWN")
    print("-" * 40)
    for channel, stats in channel_stats.items():
        roas = stats['revenue_attributed'] / stats['cost'] if stats['cost'] > 0 else 0
        cpa = stats['cost'] / stats['contributing_conversions'] if stats['contributing_conversions'] > 0 else 0
        print(f"{channel.upper()}:")
        print(f"  • Touchpoints: {stats['touchpoints']:,}")
        print(f"  • Cost: ${stats['cost']:,.2f}")
        print(f"  • Contributing conversions: {stats['contributing_conversions']}")
        print(f"  • ROAS: {roas:.2f}x")
        print(f"  • CPA: ${cpa:.2f}")
        print()
    
    # Simulate OpenAI analysis
    print("🤖 Running AI-Powered Attribution Analysis...")
    mock_client = MockOpenAIClient()
    
    print("🎯 AI ATTRIBUTION ANALYSIS RESULTS")
    print("-" * 40)
    
    # Generate analysis prompt (simulated)
    analysis_prompt = f"""
    CAMPAIGN PERFORMANCE OVERVIEW:
    - Total touchpoints: {len(touchpoints):,}
    - Total conversions: {len(conversions):,}
    - Total revenue: ${total_revenue:,.2f}
    - Total marketing cost: ${total_cost:,.2f}
    - Overall ROAS: {overall_roas:.2f}x
    - Conversion rate: {conversion_rate:.2f}%

    CHANNEL PERFORMANCE BREAKDOWN:
    """
    
    attribution_analysis = mock_client.chat(analysis_prompt)
    print(attribution_analysis)
    print()
    
    # Generate optimization recommendations
    print("🚀 AI OPTIMIZATION RECOMMENDATIONS")
    print("-" * 40)
    
    optimization_prompt = f"""
    OPTIMIZATION REQUIREMENTS:
    - Overall ROAS: {overall_roas:.2f}x
    - Conversion Rate: {conversion_rate:.2f}%
    - Total Revenue: ${total_revenue:,.2f}
    - Total Cost: ${total_cost:,.2f}
    """
    
    optimization_plan = mock_client.chat(optimization_prompt + "OPTIMIZATION REQUIREMENTS")
    print(optimization_plan)
    print()
    
    # Create causal attribution model
    print("🧠 CAUSAL MODEL ANALYSIS")
    print("-" * 28)
    
    try:
        causal_model = create_causal_attribution_model(touchpoints, conversions)
        
        # Scenario 1: Enhanced email marketing
        print("✉️ SCENARIO 1: Enhanced Email Marketing")
        print("-" * 40)
        email_scenario = causal_model.simulate_do({
            "email_effectiveness": "30% of touchpoints with personalization and segmentation"
        })
        print(email_scenario)
        print()
        
        # Scenario 2: Search optimization
        print("🔍 SCENARIO 2: Search Advertising Optimization")
        print("-" * 45)
        search_scenario = causal_model.simulate_do({
            "search_intent": "25% of touchpoints with improved keyword targeting",
            "cost_efficiency": "increased ROAS through bid optimization"
        })
        print(search_scenario)
        print()
        
        # Scenario 3: Cross-channel integration
        print("🔗 SCENARIO 3: Integrated Cross-Channel Strategy")
        print("-" * 48)
        integration_scenario = causal_model.simulate_do({
            "channel_synergy": "enhanced multi-channel coordination with unified messaging",
            "customer_journey_length": "optimized journey paths reducing friction"
        })
        print(integration_scenario)
        print()
        
    except Exception as e:
        print(f"   ❌ Causal model analysis failed: {e}")
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'dataset_summary': {
            'touchpoints_count': len(touchpoints),
            'conversions_count': len(conversions),
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'overall_roas': overall_roas,
            'conversion_rate': conversion_rate
        },
        'channel_performance': channel_stats,
        'ai_analysis': attribution_analysis,
        'optimization_recommendations': optimization_plan
    }
    
    try:
        with open('marketing_attribution_demo_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print("💾 Results saved to: marketing_attribution_demo_results.json")
    except Exception as e:
        print(f"   ⚠️ Could not save results: {e}")
    
    print()
    print("🎯 DEMO COMPLETE - KEY TAKEAWAYS")
    print("-" * 35)
    print("✅ Generated realistic 90-day attribution dataset")
    print("✅ Analyzed cross-channel performance and synergies")  
    print("✅ Provided AI-powered optimization recommendations")
    print("✅ Demonstrated causal relationship modeling")
    print("✅ Showed quantified ROI projections and budget allocation")
    print()
    print("🔗 To run with actual OpenAI API:")
    print("   1. Set OPENAI_API_KEY environment variable")
    print("   2. Set OPENAI_PROJECT_ID (optional)")
    print("   3. Run: python examples/marketing_attribution_openai.py")
    print()
    print("📚 For more examples, see: USAGE_EXAMPLES.md")

if __name__ == "__main__":
    main()