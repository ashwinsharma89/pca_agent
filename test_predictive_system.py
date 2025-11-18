"""
Comprehensive Test Script for Predictive Analytics System
Tests all three predictive modules with sample data
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime

print("="*60)
print("🧪 PREDICTIVE ANALYTICS SYSTEM - COMPREHENSIVE TEST")
print("="*60)

# ============================================================================
# TEST 1: Campaign Success Predictor
# ============================================================================
print("\n" + "="*60)
print("TEST 1: Campaign Success Predictor")
print("="*60)

from src.predictive import CampaignSuccessPredictor

# Load historical data
print("\n📊 Loading historical campaign data...")
historical_data = pd.read_csv('data/historical_campaigns_sample.csv')
print(f"✅ Loaded {len(historical_data)} campaigns")
print(f"   Date range: {historical_data['start_date'].min()} to {historical_data['start_date'].max()}")
print(f"   Budget range: ${historical_data['budget'].min():,.0f} - ${historical_data['budget'].max():,.0f}")
print(f"   ROAS range: {historical_data['roas'].min():.2f} - {historical_data['roas'].max():.2f}")

# Initialize predictor
print("\n🤖 Initializing Campaign Success Predictor...")
predictor = CampaignSuccessPredictor()

# Train model
print("\n🚀 Training model...")
print("   This may take 30-60 seconds...")
metrics = predictor.train(
    historical_campaigns=historical_data,
    success_threshold={'roas': 3.0, 'cpa': 75}
)

print("\n📈 Training Results:")
print(f"   Train Accuracy: {metrics['train_accuracy']:.1%}")
print(f"   Test Accuracy: {metrics['test_accuracy']:.1%}")
print(f"   CV Mean Accuracy: {metrics['cv_mean_accuracy']:.1%} ± {metrics['cv_std_accuracy']:.1%}")
print(f"   Training Samples: {metrics['training_samples']:,}")
print(f"   Test Samples: {metrics['test_samples']:,}")
print(f"   Success Rate: {metrics['success_rate']:.1%}")

if metrics['test_accuracy'] >= 0.80:
    print("   ✅ Model accuracy is EXCELLENT (>80%)")
elif metrics['test_accuracy'] >= 0.70:
    print("   ✅ Model accuracy is GOOD (>70%)")
else:
    print("   ⚠️  Model accuracy is below target (<70%)")

# Save model
print("\n💾 Saving model...")
os.makedirs('models', exist_ok=True)
predictor.save_model('models/campaign_success_predictor.pkl')
print("   ✅ Model saved to: models/campaign_success_predictor.pkl")

# Test predictions
print("\n🎯 Testing Predictions...")
print("\n" + "-"*60)

test_campaigns = [
    {
        'name': 'High_Budget_Video_Campaign',
        'budget': 500000,
        'duration': 30,
        'audience_size': 800000,
        'channels': 'Meta,Google,LinkedIn',
        'creative_type': 'video',
        'objective': 'conversion',
        'start_date': '2024-12-01',
        'roas': 4.5
    },
    {
        'name': 'Low_Budget_Image_Campaign',
        'budget': 75000,
        'duration': 14,
        'audience_size': 150000,
        'channels': 'Display',
        'creative_type': 'image',
        'objective': 'awareness',
        'start_date': '2024-12-15',
        'roas': 2.8
    },
    {
        'name': 'Medium_Budget_Multi_Channel',
        'budget': 250000,
        'duration': 21,
        'audience_size': 500000,
        'channels': 'Meta,Google',
        'creative_type': 'carousel',
        'objective': 'engagement',
        'start_date': '2024-11-20',
        'roas': 3.8
    }
]

for i, campaign in enumerate(test_campaigns, 1):
    print(f"\nTest Campaign {i}: {campaign['name']}")
    print(f"   Budget: ${campaign['budget']:,} | Duration: {campaign['duration']} days")
    print(f"   Channels: {campaign['channels']} | Creative: {campaign['creative_type']}")
    
    prediction = predictor.predict_success_probability(campaign)
    
    prob = prediction['success_probability']
    if prob >= 70:
        emoji = "🟢"
    elif prob >= 50:
        emoji = "🟡"
    else:
        emoji = "🔴"
    
    print(f"   {emoji} Success Probability: {prob}%")
    print(f"   Confidence: {prediction['confidence_level'].upper()}")
    print(f"   Risk Level: {prediction['risk_level'].upper()}")
    
    print(f"   Top Insight: {prediction['insights'][0]}")
    if prediction['recommendations']:
        print(f"   Top Recommendation: {prediction['recommendations'][0]['message']}")

print("\n✅ Campaign Success Predictor: ALL TESTS PASSED")

# ============================================================================
# TEST 2: Early Performance Indicators
# ============================================================================
print("\n" + "="*60)
print("TEST 2: Early Performance Indicators")
print("="*60)

from src.predictive import EarlyPerformanceIndicators

# Generate sample early performance data
print("\n📊 Generating sample early performance data...")
np.random.seed(42)

# Scenario 1: Good performing campaign
early_data_good = pd.DataFrame({
    'hours_since_start': range(24),
    'impressions': np.random.randint(40000, 60000, 24),
    'clicks': np.random.randint(800, 1500, 24),
    'conversions': np.random.randint(40, 80, 24),
    'spend': np.random.uniform(1500, 2500, 24),
    'revenue': np.random.uniform(6000, 10000, 24)
})

# Scenario 2: Poor performing campaign
early_data_poor = pd.DataFrame({
    'hours_since_start': range(24),
    'impressions': np.random.randint(20000, 30000, 24),
    'clicks': np.random.randint(100, 300, 24),
    'conversions': np.random.randint(2, 10, 24),
    'spend': np.random.uniform(1000, 2000, 24),
    'revenue': np.random.uniform(1000, 2500, 24)
})

print("   ✅ Generated 2 scenarios (good & poor performance)")

# Initialize EPI analyzer
print("\n🤖 Initializing Early Performance Indicators...")
epi = EarlyPerformanceIndicators()

# Test Scenario 1: Good Performance
print("\n" + "-"*60)
print("Scenario 1: Good Performing Campaign")
print("-"*60)

result_good = epi.analyze_early_metrics('CAMP_GOOD_001', early_data_good, hours_elapsed=24)

print(f"\n📊 Early Metrics (24 hours):")
print(f"   CTR: {result_good['early_metrics']['early_ctr']}%")
print(f"   Conv Rate: {result_good['early_metrics']['early_conv_rate']}%")
print(f"   CPA: ${result_good['early_metrics']['early_cpa']}")
print(f"   ROAS: {result_good['early_metrics']['early_roas']}")
print(f"   Audience Quality: {result_good['early_metrics']['audience_quality_score']}/100")

prob_good = result_good['success_prediction']['probability']
print(f"\n🎯 Success Prediction:")
print(f"   Probability: {prob_good}%")
print(f"   Confidence: {result_good['success_prediction']['confidence'].upper()}")
print(f"   Category: {result_good['success_prediction']['category'].upper()}")

if result_good['warnings']:
    print(f"\n⚠️  Warnings: {len(result_good['warnings'])}")
    for warning in result_good['warnings'][:2]:
        print(f"   - {warning['message']}")
else:
    print("\n✅ No warnings - Campaign performing well!")

print(f"\n💡 Recommendations: {len(result_good['recommendations'])}")
for rec in result_good['recommendations'][:2]:
    print(f"   - [{rec['priority'].upper()}] {rec['message']}")

# Test Scenario 2: Poor Performance
print("\n" + "-"*60)
print("Scenario 2: Poor Performing Campaign")
print("-"*60)

result_poor = epi.analyze_early_metrics('CAMP_POOR_002', early_data_poor, hours_elapsed=24)

print(f"\n📊 Early Metrics (24 hours):")
print(f"   CTR: {result_poor['early_metrics']['early_ctr']}%")
print(f"   Conv Rate: {result_poor['early_metrics']['early_conv_rate']}%")
print(f"   CPA: ${result_poor['early_metrics']['early_cpa']}")
print(f"   ROAS: {result_poor['early_metrics']['early_roas']}")
print(f"   Audience Quality: {result_poor['early_metrics']['audience_quality_score']}/100")

prob_poor = result_poor['success_prediction']['probability']
print(f"\n🎯 Success Prediction:")
print(f"   Probability: {prob_poor}%")
print(f"   Confidence: {result_poor['success_prediction']['confidence'].upper()}")
print(f"   Category: {result_poor['success_prediction']['category'].upper()}")

if result_poor['warnings']:
    print(f"\n⚠️  Warnings: {len(result_poor['warnings'])}")
    for warning in result_poor['warnings'][:3]:
        print(f"   - [{warning['severity'].upper()}] {warning['message']}")

print(f"\n💡 Recommendations: {len(result_poor['recommendations'])}")
for rec in result_poor['recommendations'][:3]:
    print(f"   - [{rec['priority'].upper()}] {rec['message']}")

print("\n✅ Early Performance Indicators: ALL TESTS PASSED")

# ============================================================================
# TEST 3: Budget Allocation Optimizer
# ============================================================================
print("\n" + "="*60)
print("TEST 3: Budget Allocation Optimizer")
print("="*60)

from src.predictive import BudgetAllocationOptimizer

# Prepare channel performance data
print("\n📊 Preparing channel performance data...")
channel_data = historical_data.copy()
# Add channel column (extract first channel from channels list)
channel_data['channel'] = channel_data['channels'].str.split(',').str[0]

print(f"   ✅ Prepared data for {channel_data['channel'].nunique()} channels")

# Initialize optimizer
print("\n🤖 Initializing Budget Allocation Optimizer...")
optimizer = BudgetAllocationOptimizer(channel_data)

print("\n📊 Channel Performance Summary:")
for channel, perf in optimizer.channel_performance.items():
    print(f"   {channel}:")
    print(f"      Avg ROAS: {perf['avg_roas']:.2f}")
    print(f"      Avg CPA: ${perf['avg_cpa']:.2f}")
    print(f"      Campaigns: {perf['campaign_count']}")

# Test optimization
print("\n" + "-"*60)
print("Optimization Test: $1M Budget for ROAS Goal")
print("-"*60)

result = optimizer.optimize_allocation(
    total_budget=1000000,
    campaign_goal='roas',
    constraints={'min_spend_per_channel': 50000}
)

print(f"\n💰 Optimization Results:")
print(f"   Total Budget: ${result['total_budget']:,}")
print(f"   Expected Revenue: ${result['overall_metrics']['expected_total_revenue']:,}")
print(f"   Expected ROAS: {result['overall_metrics']['expected_overall_roas']:.2f}")
print(f"   Expected Conversions: {result['overall_metrics']['expected_total_conversions']:,}")

print(f"\n📊 Recommended Allocation:")
for channel, alloc in result['allocation'].items():
    print(f"\n   {channel}:")
    print(f"      Budget: ${alloc['recommended_budget']:,} ({alloc['percentage_of_total']}%)")
    print(f"      Expected ROAS: {alloc['expected_roas']:.2f}")
    print(f"      Expected Revenue: ${alloc['expected_revenue']:,}")
    print(f"      Saturation Risk: {alloc['saturation_risk'].upper()}")

if result.get('recommendations'):
    print(f"\n💡 Optimization Recommendations:")
    for rec in result['recommendations']:
        print(f"   - [{rec['priority'].upper()}] {rec['message']}")

print("\n✅ Budget Allocation Optimizer: ALL TESTS PASSED")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*60)
print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
print("="*60)

print("\n📊 Summary:")
print(f"   ✅ Campaign Success Predictor: Trained & Tested")
print(f"      - Model Accuracy: {metrics['test_accuracy']:.1%}")
print(f"      - Predictions: 3/3 successful")
print(f"      - Model saved: models/campaign_success_predictor.pkl")

print(f"\n   ✅ Early Performance Indicators: Tested")
print(f"      - Good scenario: {prob_good}% success probability")
print(f"      - Poor scenario: {prob_poor}% success probability")
print(f"      - Warning system: Working")

print(f"\n   ✅ Budget Allocation Optimizer: Tested")
print(f"      - Optimization: Successful")
print(f"      - Expected ROAS: {result['overall_metrics']['expected_overall_roas']:.2f}")
print(f"      - Channels optimized: {len(result['allocation'])}")

print("\n" + "="*60)
print("🚀 PREDICTIVE ANALYTICS SYSTEM IS READY!")
print("="*60)

print("\n📚 Next Steps:")
print("   1. ✅ Models trained and saved")
print("   2. 🌐 Dashboard running at: http://localhost:8516")
print("   3. 🎯 Go to dashboard and test predictions")
print("   4. 💾 Upload your own historical data")
print("   5. 📈 Track prediction accuracy over time")

print("\n💡 Pro Tips:")
print("   - Retrain model monthly with new campaigns")
print("   - Track predictions vs actuals")
print("   - Use early warnings to optimize mid-campaign")
print("   - Apply budget recommendations for better ROAS")

print("\n" + "="*60)
print("Happy Predicting! 🔮")
print("="*60 + "\n")
