# File: src/core/advanced_ai_model.py
import logging
import tensorflow as tf
import os
from pathlib import Path

def load_model(model_path=None):
    """Load the TensorFlow model for task optimization"""
    logger = logging.getLogger(__name__)
    
    try:
        if not model_path:
            model_path = str(Path(__file__).parent.parent.parent / 'models' / 'advanced_model.h5')
            
        if not os.path.exists(model_path):
            logger.warning(f"Model not found at {model_path}, creating new model")
            return create_default_model()
            
        model = tf.keras.models.load_model(model_path)
        logger.info("Successfully loaded AI model")
        return model
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return create_default_model()

def create_default_model():
    """Create a default model if none exists"""
    logger = logging.getLogger(__name__)
    
    try:
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(4,)),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy'
        )
        
        logger.info("Created new default model")
        return model
        
    except Exception as e:
        logger.error(f"Error creating default model: {str(e)}")
        raise
