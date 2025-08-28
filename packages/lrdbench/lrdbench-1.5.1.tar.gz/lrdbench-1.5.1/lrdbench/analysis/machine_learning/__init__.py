"""
Machine Learning Estimators for Long-Range Dependence Analysis

This package provides machine learning-based approaches for estimating
Hurst parameters and long-range dependence characteristics from time series data.

The estimators include:
- Neural Network Regression
- Random Forest Regression
- Support Vector Regression
- Gradient Boosting Regression
- Convolutional Neural Networks
- Recurrent Neural Networks (LSTM/GRU)
- Transformer-based approaches
"""

from .base_ml_estimator import BaseMLEstimator
from .neural_network_estimator import NeuralNetworkEstimator
from .random_forest_estimator import RandomForestEstimator
from .svr_estimator import SVREstimator
from .gradient_boosting_estimator import GradientBoostingEstimator
from .cnn_estimator import CNNEstimator
from .lstm_estimator import LSTMEstimator
from .gru_estimator import GRUEstimator
from .transformer_estimator import TransformerEstimator

__all__ = [
    "BaseMLEstimator",
    "NeuralNetworkEstimator",
    "RandomForestEstimator",
    "SVREstimator",
    "GradientBoostingEstimator",
    "CNNEstimator",
    "LSTMEstimator",
    "GRUEstimator",
    "TransformerEstimator",
]
