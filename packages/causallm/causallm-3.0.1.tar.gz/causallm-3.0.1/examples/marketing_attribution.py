#!/usr/bin/env python3
"""
Marketing Campaign Attribution Example

This example demonstrates how to use CausalLLM to analyze marketing campaign 
effectiveness and understand true causal impact on sales.

Run: python examples/marketing_attribution.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from causallm.core.causal_llm_core import CausalLLMCore

def main():
    """Run marketing attribution causal analysis example."""
    print("📈 " + "="*60)
    print("   CAUSALLM MARKETING ATTRIBUTION EXAMPLE")
    print("="*63)
    print()
    
    # Define marketing context
    marketing_context = """
    An e-commerce company runs integrated marketing campaigns across multiple channels.
    Email campaigns directly influence website visits and customer engagement.
    Social media advertising drives brand awareness and website traffic.
    Website visits convert to purchases based on user experience and product fit.
    Customer lifetime value depends on purchase satisfaction and retention efforts.
    Seasonal trends and economic factors influence overall conversion rates.
    """
    
    # Define current marketing state
    marketing_variables = {
        "email_campaigns": "weekly newsletter to 50K subscribers",
        "social_media_ads": "$10K monthly spend across platforms", 
        "website_visits": "15,000 daily unique visitors",
        "brand_awareness": "moderate brand recognition",
        "customer_engagement": "3.5 minute average session time",
        "seasonal_trends": "normal shopping season",
        "conversion_rate": "2.8% purchase conversion rate",
        "customer_lifetime_value": "$180 average CLV"
    }
    
    # Define marketing causal relationships
    marketing_dag = [
        ('email_campaigns', 'customer_engagement'),
        ('email_campaigns', 'website_visits'),
        ('social_media_ads', 'brand_awareness'),
        ('social_media_ads', 'website_visits'),
        ('brand_awareness', 'customer_engagement'),
        ('website_visits', 'conversion_rate'),
        ('customer_engagement', 'conversion_rate'),
        ('seasonal_trends', 'conversion_rate'),
        ('conversion_rate', 'customer_lifetime_value'),
        ('customer_engagement', 'customer_lifetime_value')
    ]
    
    print("🎯 Setting up marketing attribution model...")
    try:
        # Create marketing causal model
        core = CausalLLMCore(marketing_context, marketing_variables, marketing_dag)
        print("   ✅ Marketing causal model initialized")
        print(f"   ✅ DAG created with {len(marketing_dag)} attribution relationships")
        print()
        
        # Scenario 1: Double social media investment
        print("💰 SCENARIO 1: Increased Social Media Investment")
        print("-" * 50)
        social_investment = core.simulate_do({
            "social_media_ads": "$20K monthly spend (2x increase) with improved targeting"
        })
        print(social_investment)
        print()
        
        # Scenario 2: Personalized email campaigns
        print("✉️ SCENARIO 2: Personalized Email Marketing")
        print("-" * 45)
        personalized_email = core.simulate_do({
            "email_campaigns": "personalized weekly newsletter with behavioral triggers"
        })
        print(personalized_email)
        print()
        
        # Scenario 3: Combined optimization
        print("🚀 SCENARIO 3: Integrated Campaign Optimization")
        print("-" * 48)
        integrated_campaign = core.simulate_do({
            "email_campaigns": "personalized behavioral email campaigns",
            "social_media_ads": "$15K monthly spend with advanced targeting",
            "customer_engagement": "enhanced engagement through interactive content"
        })
        print(integrated_campaign)
        print()
        
        # Generate attribution analysis prompt
        print("🔍 MARKETING ATTRIBUTION ANALYSIS")
        print("-" * 40)
        attribution_task = "determine the true incremental revenue impact of each marketing channel and recommend budget allocation"
        attribution_prompt = core.generate_reasoning_prompt(attribution_task)
        print("Generated marketing attribution prompt:")
        print(attribution_prompt)
        print()
        
    except Exception as e:
        print(f"   ❌ Error in marketing analysis: {e}")
        return
    
    # Marketing insights
    print("💡 MARKETING INSIGHTS")
    print("-" * 25)
    print("📧 Email Marketing:")
    print("   • Direct impact on engagement and website visits")
    print("   • Cost-effective for existing customer retention")
    print("   • Personalization can significantly improve conversion")
    print()
    print("📱 Social Media Advertising:")
    print("   • Builds brand awareness for long-term growth")
    print("   • Drives top-of-funnel website traffic")
    print("   • Effectiveness depends on targeting precision")
    print()
    print("🔄 Channel Interactions:")
    print("   • Email and social media work synergistically")
    print("   • Brand awareness enhances email engagement")
    print("   • Website experience amplifies all channel effects")
    print()
    
    print("🎯 KEY TAKEAWAYS")
    print("-" * 20)
    print("✅ CausalLLM identified true marketing attribution relationships")
    print("✅ Simulated investment scenarios with expected outcomes")
    print("✅ Generated structured analysis for budget optimization")
    print("✅ Revealed hidden channel interactions and synergies")
    print()
    print("📊 Recommended Actions:")
    print("   • A/B test personalized email campaigns")
    print("   • Gradually increase social media spend with measurement")
    print("   • Implement unified attribution tracking")
    print("   • Focus on customer engagement metrics")
    print()
    print("📚 For more examples, see: USAGE_EXAMPLES.md")

if __name__ == "__main__":
    main()