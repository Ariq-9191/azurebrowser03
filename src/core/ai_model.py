# File: src/core/ai_model.py
import numpy as np
import tensorflow as tf
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Any
import joblib
from pathlib import Path
import logging

class BehaviorPredictionModel:
    def __init__(self, model_path=None):
        self.logger = logging.getLogger(__name__)
        self.rf_model = RandomForestClassifier(n_estimators=100, max_depth=10)
        self.nn_model = self._build_nn_model()
        self.scaler = StandardScaler()
        self.model_path = model_path or str(Path(__file__).parent.parent.parent / 'models' / 'behavior_model.pkl')
        self._load_model()
        
    def _build_nn_model(self) -> tf.keras.Model:
        """Build neural network for complex behavior analysis"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(10,)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model
        
    def prepare_training_data(self, interaction_logs: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Extract advanced features from interaction logs"""
        features = []
        labels = []
        
        for log in interaction_logs:
            feature = [
                log.get('watch_duration', 0),
                log.get('scroll_count', 0),
                log.get('interaction_frequency', 0),
                log.get('mouse_movement_speed', 0),
                log.get('typing_speed', 0),
                log.get('pause_frequency', 0),
                log.get('click_accuracy', 0),
                log.get('scroll_pattern_regularity', 0),
                log.get('interaction_consistency', 0),
                log.get('session_duration', 0)
            ]
            features.append(feature)
            labels.append(log.get('is_human', 0))
            
        features = np.array(features)
        features = self.scaler.fit_transform(features)
        return features, np.array(labels)
        
    def train(self, features: np.ndarray, labels: np.ndarray):
        """Train both RF and NN models"""
        # Train Random Forest
        self.rf_model.fit(features, labels)
        
        # Train Neural Network
        self.nn_model.fit(
            features, labels,
            epochs=50,
            batch_size=32,
            validation_split=0.2,
            verbose=0
        )
        
        # Save models
        self._save_model()
        
    def predict_human_like_behavior(self, interaction_data: np.ndarray) -> float:
        """Ensemble prediction combining RF and NN"""
        interaction_data = self.scaler.transform(interaction_data)
        
        rf_pred = self.rf_model.predict_proba(interaction_data)[:, 1]
        nn_pred = self.nn_model.predict(interaction_data).flatten()
        
        # Weighted ensemble
        return 0.6 * rf_pred + 0.4 * nn_pred
        
    def _save_model(self):
        """Save models and scaler"""
        model_data = {
            'rf_model': self.rf_model,
            'scaler': self.scaler
        }
        joblib.dump(model_data, self.model_path)
        self.nn_model.save(str(Path(self.model_path).parent / 'nn_model.h5'))
        
    def _load_model(self):
        """Load saved models if available"""
        try:
            model_data = joblib.load(self.model_path)
            self.rf_model = model_data['rf_model']
            self.scaler = model_data['scaler']
            nn_path = str(Path(self.model_path).parent / 'nn_model.h5')
            if Path(nn_path).exists():
                self.nn_model = tf.keras.models.load_model(nn_path)
        except:
            self.logger.warning("No saved models found, using new models")