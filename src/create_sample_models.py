import joblib
import tensorflow as tf
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier

def create_sample_models():
	# Create directory if it doesn't exist
	base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	models_dir = os.path.join(base_dir, 'models')
	os.makedirs(models_dir, exist_ok=True)
	
	# Create and save behavior model (sklearn)
	print("Creating behavior model...")
	X = np.random.rand(100, 4)  # Sample features
	y = np.random.randint(0, 2, 100)  # Binary classification
	behavior_model = RandomForestClassifier(n_estimators=10)
	behavior_model.fit(X, y)
	
	behavior_model_path = os.path.join(models_dir, 'behavior_model.pkl')
	joblib.dump(behavior_model, behavior_model_path)
	print(f"Saved behavior model to {behavior_model_path}")
	
	# Create and save advanced model (tensorflow)
	print("\nCreating advanced model...")
	model = tf.keras.Sequential([
		tf.keras.layers.Dense(64, activation='relu', input_shape=(4,)),
		tf.keras.layers.Dense(32, activation='relu'),
		tf.keras.layers.Dense(1, activation='sigmoid')
	])
	model.compile(optimizer='adam', loss='binary_crossentropy')
	
	# Train with some dummy data
	X_train = np.random.rand(100, 4)
	y_train = np.random.randint(0, 2, 100)
	model.fit(X_train, y_train, epochs=1, verbose=0)
	
	advanced_model_path = os.path.join(models_dir, 'advanced_model.h5')
	model.save(advanced_model_path)
	print(f"Saved advanced model to {advanced_model_path}")

if __name__ == "__main__":
	create_sample_models()