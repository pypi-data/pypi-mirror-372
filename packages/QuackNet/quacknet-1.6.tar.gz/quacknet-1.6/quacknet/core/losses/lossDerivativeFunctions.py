import numpy as np
from quacknet.core.activations.activationDerivativeFunctions import SoftMaxDerivative

def MSEDerivative(value, trueValue, sizeOfLayer):
    """
    Calculates the derivative of the Mean Squared Error (MSE) loss function.

    Args:
        value (ndarray): The predicted values from the model.
        trueValue (ndarray): The true target values.
        sizeOfLayer (int): The size of the output layer.
    
    Returns:
        ndarray: The gradients of the MSE loss.
    """
    return 2 * (value - trueValue) / sizeOfLayer

def MAEDerivative(value, trueValue, sizeOfLayer):
    """
    Calculates the derivative of the Mean Absolute Error (MAE) loss function.

    Args:
        value (ndarray): The predicted values from the model.
        trueValue (ndarray): The true target values.
        sizeOfLayer (int): The size of the output layer.
    
    Returns:
        ndarray: The gradients of the MAE loss.
    """
    #summ = value - trueValue
    #if(summ > 0):
    #    return 1 / sizeOfLayer
    #elif(summ < 0):
    #    return -1 / sizeOfLayer
    #return 0
    return np.sign(value - trueValue) / sizeOfLayer

def CrossEntropyLossDerivative(value, trueVale, activationDerivative):
    """
    Calculates the derivative of the Cross Entropy loss function.

    Args:
        value (ndarray): The predicted values from the model.
        trueValue (ndarray): The true target values.
        activationDerivative (function): The derivative of the activation function.
    
    Returns:
        ndarray: The gradients of the Cross Entropy loss.
    """
    if(activationDerivative == SoftMaxDerivative):
        return value - trueVale
    return -1 * (trueVale / value)
