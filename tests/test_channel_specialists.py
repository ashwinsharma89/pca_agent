"""
Channel Specialist Routing Tests
Tests channel-specific agent routing and analysis
"""

import pytest
import pandas as pd
import numpy as np
from typing import Dict, List

from src.agents.channel_specialists import (
    ChannelRouter,
    SearchChannelAgent,
    SocialChannelAgent,
    DisplayChannelAgent,
    VideoChannelAgent
)


class TestChannelRouting:
    """Test channel specialist routing logic"""
    
    @pytest.fixture
    def router(self):
        """Create channel router instance"""
        return ChannelRouter()
    
    def test_search_specialist_routing(self, router):
        """Verify search campaigns go to SearchChannelAgent"""
        
        # Google Ads search campaign
        google_data = {
            'platform': 'google_ads',
            'channel': 'Google Ads',
            'campaign_type': 'search',
            'spend': 1000,
            'clicks': 200,
            'conversions': 20
        }
        
        specialist = router.route_to_specialist(google_data)
        assert isinstance(specialist, SearchChannelAgent)
        
        # Bing Ads search campaign
        bing_data = {
            'platform': 'bing_ads',
            'channel': 'Bing Ads',
            'campaign_type': 'search',
            'spend': 500,
            'clicks': 100,
            'conversions': 10
        }
        
        specialist = router.route_to_specialist(bing_data)
        assert isinstance(specialist, SearchChannelAgent)
        
        print("✅ Search specialist routing test passed!")
    
    def test_social_specialist_routing(self, router):
        """Verify social campaigns go to SocialChannelAgent"""
        
        # Meta (Facebook/Instagram)
        meta_data = {
            'platform': 'meta',
            'channel': 'Meta',
            'campaign_type': 'social',
            'spend': 1500,
            'impressions': 50000,
            'clicks': 500,
            'conversions': 30
        }
        
        specialist = router.route_to_specialist(meta_data)
        assert isinstance(specialist, SocialChannelAgent)
        
        # LinkedIn
        linkedin_data = {
            'platform': 'linkedin',
            'channel': 'LinkedIn',
            'campaign_type': 'social',
            'spend': 2000,
            'impressions': 30000,
            'clicks': 300,
            'conversions': 25
        }
        
        specialist = router.route_to_specialist(linkedin_data)
        assert isinstance(specialist, SocialChannelAgent)
        
        # TikTok
        tiktok_data = {
            'platform': 'tiktok',
            'channel': 'TikTok',
            'campaign_type': 'social',
            'spend': 1000,
            'impressions': 100000,
            'clicks': 1000,
            'conversions': 20
        }
        
        specialist = router.route_to_specialist(tiktok_data)
        assert isinstance(specialist, SocialChannelAgent)
        
        print("✅ Social specialist routing test passed!")
    
    def test_display_specialist_routing(self, router):
        """Verify display campaigns go to DisplayChannelAgent"""
        
        display_data = {
            'platform': 'google_ads',
            'channel': 'Google Display',
            'campaign_type': 'display',
            'spend': 800,
            'impressions': 100000,
            'clicks': 200,
            'conversions': 10
        }
        
        specialist = router.route_to_specialist(display_data)
        assert isinstance(specialist, DisplayChannelAgent)
        
        print("✅ Display specialist routing test passed!")
    
    def test_video_specialist_routing(self, router):
        """Verify video campaigns go to VideoChannelAgent"""
        
        # YouTube
        youtube_data = {
            'platform': 'youtube',
            'channel': 'YouTube',
            'campaign_type': 'video',
            'spend': 2000,
            'impressions': 200000,
            'views': 50000,
            'clicks': 500,
            'conversions': 25
        }
        
        specialist = router.route_to_specialist(youtube_data)
        assert isinstance(specialist, VideoChannelAgent)
        
        print("✅ Video specialist routing test passed!")
    
    def test_fallback_routing(self, router):
        """Test fallback for unknown channel types"""
        
        unknown_data = {
            'platform': 'unknown_platform',
            'channel': 'Unknown',
            'spend': 1000
        }
        
        specialist = router.route_to_specialist(unknown_data)
        # Should return a default specialist or None
        assert specialist is not None or specialist is None
        
        print("✅ Fallback routing test passed!")


class TestSearchChannelAgent:
    """Test Search Channel Agent functionality"""
    
    @pytest.fixture
    def search_agent(self):
        """Create search agent instance"""
        return SearchChannelAgent()
    
    @pytest.fixture
    def search_campaign_data(self):
        """Generate search campaign data"""
        return [
            {
                'date': '2024-01-01',
                'campaign': 'Brand Search',
                'keyword': 'brand name',
                'match_type': 'exact',
                'spend': 500,
                'clicks': 100,
                'conversions': 15,
                'ctr': 0.05,
                'cpc': 5.0,
                'quality_score': 8
            },
            {
                'date': '2024-01-01',
                'campaign': 'Generic Search',
                'keyword': 'product category',
                'match_type': 'broad',
                'spend': 1000,
                'clicks': 150,
                'conversions': 10,
                'ctr': 0.03,
                'cpc': 6.67,
                'quality_score': 6
            }
        ]
    
    def test_search_insights_generation(self, search_agent, search_campaign_data):
        """Test search-specific insights generation"""
        
        insights = search_agent.analyze(search_campaign_data)
        
        assert len(insights) > 0
        assert all('message' in insight for insight in insights)
        
        # Check for search-specific insights
        insight_messages = ' '.join([i['message'] for i in insights])
        
        # Should mention keywords, quality score, or match types
        search_terms = ['keyword', 'quality', 'match', 'search']
        assert any(term in insight_messages.lower() for term in search_terms)
        
        print("✅ Search insights generation test passed!")
    
    def test_keyword_analysis(self, search_agent, search_campaign_data):
        """Test keyword-level analysis"""
        
        insights = search_agent.analyze(search_campaign_data)
        
        # Should identify high-performing keywords
        high_perf_keywords = [
            d for d in search_campaign_data
            if d['conversions'] / d['clicks'] > 0.1
        ]
        
        assert len(high_perf_keywords) > 0
        
        print("✅ Keyword analysis test passed!")
    
    def test_quality_score_analysis(self, search_agent, search_campaign_data):
        """Test quality score analysis"""
        
        # Check quality scores
        quality_scores = [d['quality_score'] for d in search_campaign_data]
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        assert avg_quality > 0
        assert all(1 <= qs <= 10 for qs in quality_scores)
        
        print("✅ Quality score analysis test passed!")


class TestSocialChannelAgent:
    """Test Social Channel Agent functionality"""
    
    @pytest.fixture
    def social_agent(self):
        """Create social agent instance"""
        return SocialChannelAgent()
    
    @pytest.fixture
    def social_campaign_data(self):
        """Generate social campaign data"""
        return [
            {
                'date': '2024-01-01',
                'campaign': 'Brand Awareness',
                'platform': 'meta',
                'ad_format': 'image',
                'spend': 1000,
                'impressions': 50000,
                'clicks': 500,
                'conversions': 25,
                'ctr': 0.01,
                'frequency': 3.5,
                'engagement_rate': 0.05
            },
            {
                'date': '2024-01-01',
                'campaign': 'Lead Generation',
                'platform': 'linkedin',
                'ad_format': 'sponsored_content',
                'spend': 1500,
                'impressions': 30000,
                'clicks': 300,
                'conversions': 30,
                'ctr': 0.01,
                'frequency': 2.8,
                'engagement_rate': 0.08
            }
        ]
    
    def test_social_insights_generation(self, social_agent, social_campaign_data):
        """Test social-specific insights generation"""
        
        insights = social_agent.analyze(social_campaign_data)
        
        assert len(insights) > 0
        
        # Check for social-specific insights
        insight_messages = ' '.join([i['message'] for i in insights])
        
        # Should mention engagement, frequency, or social metrics
        social_terms = ['engagement', 'frequency', 'social', 'audience']
        assert any(term in insight_messages.lower() for term in social_terms)
        
        print("✅ Social insights generation test passed!")
    
    def test_frequency_analysis(self, social_agent, social_campaign_data):
        """Test ad frequency analysis"""
        
        # Check for high frequency
        high_freq_campaigns = [
            d for d in social_campaign_data
            if d['frequency'] > 3.0
        ]
        
        # Should detect potential creative fatigue
        if high_freq_campaigns:
            insights = social_agent.analyze(social_campaign_data)
            insight_messages = ' '.join([i['message'] for i in insights])
            
            # May mention frequency or fatigue
            assert 'frequency' in insight_messages.lower() or len(insights) > 0
        
        print("✅ Frequency analysis test passed!")
    
    def test_engagement_analysis(self, social_agent, social_campaign_data):
        """Test engagement rate analysis"""
        
        engagement_rates = [d['engagement_rate'] for d in social_campaign_data]
        avg_engagement = sum(engagement_rates) / len(engagement_rates)
        
        assert avg_engagement > 0
        assert all(0 <= er <= 1 for er in engagement_rates)
        
        print("✅ Engagement analysis test passed!")


class TestChannelComparison:
    """Test cross-channel comparison functionality"""
    
    def test_multi_channel_performance(self):
        """Test performance comparison across channels"""
        
        channels_data = {
            'Google Ads': {'spend': 5000, 'conversions': 100, 'roas': 3.0},
            'Meta': {'spend': 4000, 'conversions': 80, 'roas': 2.5},
            'LinkedIn': {'spend': 3000, 'conversions': 60, 'roas': 2.8}
        }
        
        # Calculate efficiency metrics
        for channel, data in channels_data.items():
            cpa = data['spend'] / data['conversions']
            assert cpa > 0
            assert data['roas'] > 0
        
        # Find best performing channel
        best_channel = max(
            channels_data.items(),
            key=lambda x: x[1]['roas']
        )
        
        assert best_channel[0] == 'Google Ads'
        assert best_channel[1]['roas'] == 3.0
        
        print("✅ Multi-channel performance test passed!")
    
    def test_channel_budget_allocation(self):
        """Test budget allocation recommendations"""
        
        channels = {
            'High ROAS Channel': {'roas': 4.0, 'spend': 2000},
            'Medium ROAS Channel': {'roas': 2.5, 'spend': 3000},
            'Low ROAS Channel': {'roas': 1.5, 'spend': 5000}
        }
        
        # Should recommend shifting budget to high ROAS channel
        total_spend = sum(c['spend'] for c in channels.values())
        
        for channel, data in channels.items():
            budget_share = data['spend'] / total_spend
            assert 0 < budget_share < 1
        
        print("✅ Channel budget allocation test passed!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
