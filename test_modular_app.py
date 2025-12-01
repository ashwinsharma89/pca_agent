"""
Test modular app components.
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all component imports work."""
    print("Testing component imports...")
    
    try:
        from streamlit_components.data_loader import DataLoaderComponent
        print("✅ data_loader imports successfully")
    except Exception as e:
        print(f"❌ data_loader import failed: {e}")
        return False
    
    try:
        from streamlit_components.analysis_runner import AnalysisRunnerComponent
        print("✅ analysis_runner imports successfully")
    except Exception as e:
        print(f"❌ analysis_runner import failed: {e}")
        return False
    
    try:
        from streamlit_components.caching_strategy import CacheManager
        print("✅ caching_strategy imports successfully")
    except Exception as e:
        print(f"❌ caching_strategy import failed: {e}")
        return False
    
    try:
        from streamlit_components.smart_filters import InteractiveFilterPanel
        print("✅ smart_filters imports successfully")
    except Exception as e:
        print(f"❌ smart_filters import failed: {e}")
        return False
    
    return True


def test_analysis_agent():
    """Test that analysis agent can be imported."""
    print("\nTesting analysis agent...")
    
    try:
        from src.analytics.auto_insights import MediaAnalyticsExpert
        print("✅ MediaAnalyticsExpert imports successfully")
        return True
    except Exception as e:
        print(f"❌ MediaAnalyticsExpert import failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("MODULAR APP COMPONENT TESTS")
    print("=" * 60)
    
    results = []
    
    # Test imports
    results.append(("Component Imports", test_imports()))
    
    # Test analysis agent
    results.append(("Analysis Agent", test_analysis_agent()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYou can now run the modular app:")
        print("  streamlit run app_modular.py")
    else:
        print("\n⚠️ SOME TESTS FAILED")
    
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
