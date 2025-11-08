import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=== Full System Test ===\n")

# Test TensorFlow
print("1. Testing TensorFlow...")
try:
    import tensorflow as tf
    print(f"   [OK] TensorFlow {tf.__version__}")
except Exception as e:
    print(f"   [FAIL] {e}")

# Test Enhanced Analyzer
print("\n2. Testing Enhanced Analyzer...")
try:
    from enhanced_analyzer import EnhancedVideoAnalyzer
    analyzer = EnhancedVideoAnalyzer()
    
    if analyzer.driver_model:
        print(f"   [OK] Model loaded successfully")
        print(f"   Input: {analyzer.driver_model.input_shape}")
        print(f"   Output: {analyzer.driver_model.output_shape}")
    else:
        print(f"   [FAIL] Model not loaded")
except Exception as e:
    print(f"   [FAIL] {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
