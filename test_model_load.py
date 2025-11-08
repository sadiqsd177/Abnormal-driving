import os
import sys

print("=== Model Loading Test ===\n")

# Get script directory and change to it
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print(f"Working directory: {os.getcwd()}\n")

# Check if model files exist
models = ['driver_model_updated.h5', 'driver_model.h5']
for model in models:
    exists = os.path.exists(model)
    size = os.path.getsize(model) / (1024*1024) if exists else 0
    print(f"{model}: {'EXISTS' if exists else 'NOT FOUND'} ({size:.1f} MB)")

print("\n=== TensorFlow Test ===")
try:
    import tensorflow as tf
    from tensorflow import keras
    print(f"TensorFlow version: {tf.__version__}")
    print("TensorFlow imported successfully")
    
    print("\n=== Loading Model ===")
    for model_path in ['driver_model_updated.h5', 'driver_model.h5']:
        try:
            print(f"\nTrying {model_path}...")
            model = keras.models.load_model(model_path, compile=False)
            print(f"[SUCCESS] Model loaded: {model_path}")
            print(f"Input shape: {model.input_shape}")
            print(f"Output shape: {model.output_shape}")
            break
        except Exception as e:
            print(f"[FAILED] {type(e).__name__}: {str(e)[:100]}")
            continue
    
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
