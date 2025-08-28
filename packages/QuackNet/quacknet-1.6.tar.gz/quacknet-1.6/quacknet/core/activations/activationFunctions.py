import numpy as np

def relu(values, alpha = 0.01):
    """
    Applies Leaky Rectified Linear Unit (ReLU) activation function.

    Args:
        values (ndarray): Input array to apply leaky ReLU to.
        alpha (float, optional): Slope for negative values. Default is 0.01.
    
    Returns:
        ndarray: Array with Leaky ReLU applied to it.    
    """
    return np.maximum(values * alpha, values) 
     
def sigmoid(values):
    """
    Applies the sigmoid activation function.

    Args:
        values (ndarray): Input array to apply sigmoid.
    
    Returns:
        ndarray: Array with sigmoid applied to it.    
    """
    return 1 / (1 + np.exp(-values))

def tanH(values):
    """
    Applies the hyperbolic tangent (tanh) activation function.

    Args:
        values (ndarray): Input array to apply tanh.
    
    Returns:
        ndarray: Array with tanh applied to it.    
    """
    return np.tanh(values)

def linear(values): #Dont use too demanding on CPU
    """
    Applies the linear activation function.

    Args:
        values (ndarray): Input array.
    
    Returns:
        ndarray: Output array (same as input).    
    """
    return values

def softMax(values): 
    """
    Applies the softmax activation function.

    Args:
        values (ndarray): Input array to apply softmax.
    
    Returns:
        ndarray: Array with softmax applied to it. 

    Note:
        The function handles overflow by subtracting the maximum value from inputs.
    """
    values = np.array(values, dtype=np.float64)
    maxVal = np.max(values)
    values = values - maxVal
    summ = np.sum(np.exp(values))
    out = np.exp(values) / summ
    return out