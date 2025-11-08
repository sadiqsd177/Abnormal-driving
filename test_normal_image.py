import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from enhanced_analyzer import EnhancedVideoAnalyzer

analyzer = EnhancedVideoAnalyzer()

# Test with normal.jpg
image_path = 'uploads/normal.jpg'
if os.path.exists(image_path):
    print(f"=== Analyzing {image_path} ===\n")
    result = analyzer.analyze_image(image_path)
    
    print(f"Behaviors: {result['behaviors']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Confidence: {result['confidence']}%")
    print(f"\nWarnings:")
    for warning in result['warnings']:
        print(f"  - {warning['message']}")
else:
    print(f"Image not found: {image_path}")
