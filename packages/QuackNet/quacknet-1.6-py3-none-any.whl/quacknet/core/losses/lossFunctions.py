import math
import numpy as np

def MSELossFunction(predicted, true):
    """
    Calculates the Mean Squared Error (MSE) loss.

    Args:
        predicted (list / ndarray): The predicted values from the model.
        true (list / ndarray): The true target values.

    Returns:
        float: The mean squared error between predicted and true values.
    """
    return np.mean((np.array(true) - np.array(predicted)) ** 2)

def MAELossFunction(predicted, true):
    """
    Calculates the Mean Absolute Error (MAE) loss.

    Args:
        predicted (list / ndarray): The predicted values from the model.
        true (list / ndarray): The true target values.

    Returns:
        float: The mean absolute error between predicted and true values.
    """
    return np.mean(np.abs(np.array(true) - np.array(predicted)))

def CrossEntropyLossFunction(predicted, true):
    """
    Calculates the Cross Entropy loss.

    Args:
        predicted (list / ndarray): The predicted probabilities from the model.
        true (list / ndarray): The true target values.

    Returns:
        float: The cross entropy loss between predicted probabilities and true values.
    
    Notes:
        Predicted probabilities are clipped to the range [1e-10, 1-1e-10] to avoid numerical instability.
    """
    predicted = np.clip(predicted, 1e-10, 1-1e-10)
    return -np.sum(np.array(true) * np.log(predicted))
