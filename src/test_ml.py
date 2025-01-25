import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import joblib
import h5py
import os

def test_ml_packages():
	print("Testing ML packages:")
	
	# Test TensorFlow
	print("\n1. TensorFlow Test:")
	print(f"TensorFlow version: {tf.__version__}")
	tensor = tf.constant([[1, 2], [3, 4]])
	print("TensorFlow tensor:", tensor.numpy())
	
	# Test Pandas
	print("\n2. Pandas Test:")
	print(f"Pandas version: {pd.__version__}")
	df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
	print("Pandas DataFrame:\n", df)
	
	# Test NumPy
	print("\n3. NumPy Test:")
	print(f"NumPy version: {np.__version__}")
	arr = np.array([[1, 2], [3, 4]])
	print("NumPy array:\n", arr)
	
	# Get absolute paths for models
	base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	behavior_model_path = os.path.join(base_dir, 'models', 'behavior_model.pkl')
	advanced_model_path = os.path.join(base_dir, 'models', 'advanced_model.h5')
	
	# Test model files existence
	print("\n4. Testing Model Files:")
	try:
		# Test loading behavior model
		behavior_model = joblib.load(behavior_model_path)
		print("✓ Behavior model loaded successfully")
	except Exception as e:
		print("✗ Error loading behavior model:", str(e))
		
	try:
		# Test loading advanced model
		with h5py.File(advanced_model_path, 'r') as f:
			print("✓ Advanced model file exists and is readable")
	except Exception as e:
		print("✗ Error accessing advanced model:", str(e))

if __name__ == "__main__":
	test_ml_packages()