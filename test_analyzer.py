from enhanced_analyzer import EnhancedVideoAnalyzer
import os

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=== Testing Enhanced Analyzer ===\n")

# Initialize analyzer
analyzer = EnhancedVideoAnalyzer()

# Check if model is loaded
if analyzer.driver_model:
    print("[SUCCESS] Model loaded successfully!")
    print(f"  Model type: {type(analyzer.driver_model)}")
else:
    print("[WARNING] Model not loaded - using CV only")

# Test with sample video if exists
sample_video = "uploads/radio.mp4"
if os.path.exists(sample_video):
    print(f"\n=== Analyzing {sample_video} ===")
    result = analyzer.analyze_video(sample_video)
    print(f"\nBehaviors: {result['behaviors']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Confidence: {result['confidence']}%")
    print(f"Analysis Method: {result.get('stats', {}).get('analysis_method', 'N/A')}")
    print(f"\nWarnings:")
    for warning in result['warnings']:
        print(f"  - {warning['message']}")
else:
    print(f"\n[WARNING] Sample video not found: {sample_video}")

print("\n=== Test Complete ===")
