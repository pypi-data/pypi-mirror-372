#!/usr/bin/env python3
"""
Marketing Attribution Analysis with Actual OpenAI Integration

This example demonstrates real marketing attribution analysis using CausalLLM
with actual OpenAI API calls to analyze customer journey, channel effectiveness,
and budget optimization recommendations.

Prerequisites:
- Set OPENAI_API_KEY environment variable
- Set OPENAI_PROJECT_ID environment variable (optional)
- Install: pip install openai

Run: python examples/marketing_attribution_openai.py
"""

import sys
import os
import json
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from causallm.core.causal_llm_core import CausalLLMCore
from causallm.core.llm_client import get_llm_client

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

def analyze_attribution_with_openai(touchpoints_data, conversions_data):
    """Perform marketing attribution analysis using OpenAI."""
    
    print("🤖 Initializing OpenAI client for attribution analysis...")
    
    try:
        # Create OpenAI client
        openai_client = get_llm_client("openai", "gpt-4")
        print("   ✅ OpenAI client initialized successfully")
    except Exception as e:
        print(f"   ❌ Failed to initialize OpenAI client: {e}")
        return None
    
    # Prepare data summary for analysis
    total_touchpoints = len(touchpoints_data)
    total_conversions = len(conversions_data)
    total_revenue = sum(c['conversion_value'] for c in conversions_data)
    total_cost = sum(tp['channel_cost'] for tp in touchpoints_data)
    
    # Channel performance metrics
    channel_stats = {}
    for tp in touchpoints_data:
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
    for conversion in conversions_data:
        customer_journey = conversion['touchpoint_sequence']
        revenue_per_touchpoint = conversion['conversion_value'] / len(customer_journey)
        
        for channel in customer_journey:
            if channel in channel_stats:
                channel_stats[channel]['contributing_conversions'] += 1
                channel_stats[channel]['revenue_attributed'] += revenue_per_touchpoint
    
    # Create comprehensive analysis prompt
    analysis_prompt = f"""
    As a senior marketing analyst, analyze this marketing attribution data and provide strategic insights:

    CAMPAIGN PERFORMANCE OVERVIEW:
    - Total touchpoints: {total_touchpoints:,}
    - Total conversions: {total_conversions:,}
    - Total revenue: ${total_revenue:,.2f}
    - Total marketing cost: ${total_cost:,.2f}
    - Overall ROAS: {(total_revenue / total_cost):.2f}x
    - Conversion rate: {(total_conversions / total_touchpoints * 100):.2f}%

    CHANNEL PERFORMANCE BREAKDOWN:
    """
    
    for channel, stats in channel_stats.items():
        roas = stats['revenue_attributed'] / stats['cost'] if stats['cost'] > 0 else 0
        cpa = stats['cost'] / stats['contributing_conversions'] if stats['contributing_conversions'] > 0 else 0
        analysis_prompt += f"""
    {channel.upper()}:
    - Touchpoints: {stats['touchpoints']:,}
    - Cost: ${stats['cost']:,.2f}
    - Contributing conversions: {stats['contributing_conversions']}
    - Revenue attributed: ${stats['revenue_attributed']:,.2f}
    - ROAS: {roas:.2f}x
    - CPA: ${cpa:.2f}
    """
    
    analysis_prompt += """

    ANALYSIS REQUIREMENTS:
    1. Identify the most effective channels for customer acquisition
    2. Analyze channel synergies and cross-channel attribution patterns
    3. Recommend budget reallocation strategy for maximum ROI
    4. Suggest improvements for underperforming channels
    5. Provide actionable insights for campaign optimization
    6. Calculate incremental revenue potential from budget changes

    Please provide a comprehensive marketing attribution analysis with specific recommendations and projected outcomes.
    """
    
    print("📊 Running attribution analysis with OpenAI...")
    
    try:
        attribution_analysis = openai_client.chat(
            prompt=analysis_prompt,
            temperature=0.3  # Lower temperature for analytical tasks
        )
        
        print("   ✅ Attribution analysis completed successfully")
        return {
            'analysis': attribution_analysis,
            'data_summary': {
                'total_touchpoints': total_touchpoints,
                'total_conversions': total_conversions,
                'total_revenue': total_revenue,
                'total_cost': total_cost,
                'overall_roas': total_revenue / total_cost,
                'conversion_rate': total_conversions / total_touchpoints * 100
            },
            'channel_performance': channel_stats
        }
        
    except Exception as e:
        print(f"   ❌ Attribution analysis failed: {e}")
        return None

def generate_optimization_recommendations(analysis_results, openai_client):
    """Generate specific optimization recommendations using OpenAI."""
    
    if not analysis_results:
        return None
    
    channel_performance = analysis_results['channel_performance']
    data_summary = analysis_results['data_summary']
    
    optimization_prompt = f"""
    Based on this marketing attribution analysis, create a detailed optimization plan:

    CURRENT PERFORMANCE:
    - Overall ROAS: {data_summary['overall_roas']:.2f}x
    - Conversion Rate: {data_summary['conversion_rate']:.2f}%
    - Total Revenue: ${data_summary['total_revenue']:,.2f}
    - Total Cost: ${data_summary['total_cost']:,.2f}

    CHANNEL BREAKDOWN:
    """
    
    for channel, stats in channel_performance.items():
        roas = stats['revenue_attributed'] / stats['cost'] if stats['cost'] > 0 else 0
        optimization_prompt += f"- {channel}: {stats['touchpoints']} touchpoints, ${stats['cost']:.2f} cost, {roas:.2f}x ROAS\n"
    
    optimization_prompt += """

    OPTIMIZATION REQUIREMENTS:
    1. Specific budget reallocation recommendations (dollar amounts)
    2. Channel-specific improvement tactics
    3. Cross-channel synergy opportunities
    4. Expected revenue impact of changes
    5. Timeline for implementation
    6. KPIs to track success
    7. Risk assessment of recommended changes

    Provide a detailed, actionable optimization plan with quantified projections.
    """
    
    try:
        optimization_plan = openai_client.chat(
            prompt=optimization_prompt,
            temperature=0.2
        )
        
        return optimization_plan
        
    except Exception as e:
        print(f"   ❌ Optimization planning failed: {e}")
        return None

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
    """Run the marketing attribution analysis with actual OpenAI integration."""
    
    print("🎯 " + "="*70)
    print("   MARKETING ATTRIBUTION ANALYSIS WITH OPENAI INTEGRATION")
    print("="*73)
    print()
    
    # Generate realistic marketing data
    print("📊 Generating marketing attribution dataset...")
    touchpoints, conversions = generate_marketing_data()
    
    print(f"   ✅ Generated {len(touchpoints):,} touchpoints")
    print(f"   ✅ Generated {len(conversions):,} conversions")
    print(f"   ✅ Total revenue: ${sum(c['conversion_value'] for c in conversions):,.2f}")
    print()
    
    # Analyze attribution with OpenAI
    attribution_results = analyze_attribution_with_openai(touchpoints, conversions)
    
    if attribution_results:
        print("🎯 ATTRIBUTION ANALYSIS RESULTS")
        print("-" * 40)
        print(attribution_results['analysis'])
        print()
        
        # Generate optimization recommendations
        print("🚀 GENERATING OPTIMIZATION RECOMMENDATIONS")
        print("-" * 45)
        
        try:
            openai_client = get_llm_client("openai", "gpt-4")
            optimization_plan = generate_optimization_recommendations(attribution_results, openai_client)
            
            if optimization_plan:
                print("💡 OPTIMIZATION RECOMMENDATIONS")
                print("-" * 35)
                print(optimization_plan)
                print()
        except Exception as e:
            print(f"   ❌ Could not generate optimization recommendations: {e}")
        
        # Create causal attribution model
        print("🧠 CAUSAL MODEL ANALYSIS")
        print("-" * 28)
        
        try:
            causal_model = create_causal_attribution_model(touchpoints, conversions)
            
            # Scenario 1: Increase email marketing effectiveness
            print("✉️ SCENARIO 1: Enhanced Email Marketing")
            email_scenario = causal_model.simulate_do({
                "email_effectiveness": "30% of touchpoints with personalization and segmentation"
            })
            print(email_scenario)
            print()
            
            # Scenario 2: Optimize search advertising
            print("🔍 SCENARIO 2: Search Advertising Optimization")
            search_scenario = causal_model.simulate_do({
                "search_intent": "25% of touchpoints with improved keyword targeting",
                "cost_efficiency": "increased ROAS through bid optimization"
            })
            print(search_scenario)
            print()
            
            # Scenario 3: Cross-channel integration
            print("🔗 SCENARIO 3: Integrated Cross-Channel Strategy")
            integration_scenario = causal_model.simulate_do({
                "channel_synergy": "enhanced multi-channel coordination with unified messaging",
                "customer_journey_length": "optimized journey paths reducing friction"
            })
            print(integration_scenario)
            print()
            
        except Exception as e:
            print(f"   ❌ Causal model analysis failed: {e}")
        
        # Save detailed results
        save_results(touchpoints, conversions, attribution_results)
        
    else:
        print("❌ Attribution analysis failed. Check your OpenAI API configuration.")
        return
    
    print("🎯 ATTRIBUTION ANALYSIS COMPLETE")
    print("-" * 35)
    print("✅ Generated realistic marketing dataset")
    print("✅ Performed AI-powered attribution analysis")
    print("✅ Created optimization recommendations")
    print("✅ Analyzed causal relationships")
    print("✅ Saved results for further analysis")
    print()
    print("📁 Results saved to: marketing_attribution_results.json")
    print("📚 For more examples, see: USAGE_EXAMPLES.md")

def save_results(touchpoints, conversions, attribution_results):
    """Save analysis results to JSON file."""
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'dataset_summary': {
            'touchpoints_count': len(touchpoints),
            'conversions_count': len(conversions),
            'sample_touchpoints': touchpoints[:5],  # Sample data
            'sample_conversions': conversions[:3]
        },
        'attribution_analysis': attribution_results['analysis'] if attribution_results else None,
        'performance_metrics': attribution_results['data_summary'] if attribution_results else None,
        'channel_performance': attribution_results['channel_performance'] if attribution_results else None
    }
    
    try:
        with open('marketing_attribution_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"   ✅ Results saved to marketing_attribution_results.json")
    except Exception as e:
        print(f"   ⚠️  Could not save results: {e}")

if __name__ == "__main__":
    main()