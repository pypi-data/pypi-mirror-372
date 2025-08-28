import numpy as np

def ReLUDerivative(values):
    """
    Applies Leaky Rectified Linear Unit (ReLU) derivative activation function.

    Args:
        values (ndarray): Input array to differantiate.
    
    Returns:
        ndarray: Array with Leaky ReLU derivative applied to it.    
    """
    #return np.where(values > 0, 1, 0)
    return np.where(values > 0, 1, 0.01)  # This is leaky ReLU, to prevent weight gradeints all becoming 0

def sigmoid(values): # used for sigmoid derivative and is used to remove importing from activationFunctions.py
    return 1 / (1 + np.exp(-values))

def SigmoidDerivative(values):
    """
    Applies sigmoid derivative activation function.

    Args:
        values (ndarray): Input array to differantiate.
    
    Returns:
        ndarray: Array with sigmoid derivative applied to it.    
    """
    return sigmoid(values) * (1 - sigmoid(values))

def TanHDerivative(values):
    """
    Applies hyperbolic tangent (tanh) derivative activation function.

    Args:
        values (ndarray): Input array to differantiate.
    
    Returns:
        ndarray: Array with tanh derivative applied to it.    
    """
    return 1 - (np.tanh(values) ** 2)

def LinearDerivative(values):
    """
    Applies linear derivative activation function.

    Args:
        values (ndarray): Input array to differantiate.
    
    Returns:
        ndarray: Array with linear derivative applied to it.    
    
    Note:
        the derivative is the list but every element is 1.
    """
    return np.ones_like(values)

def SoftMaxDerivative(trueValue, values):
    #from .lossDerivativeFunctions import CrossEntropyLossDerivative
    #if(lossDerivative == CrossEntropyLossDerivative):
    #    return values - trueValue
    #summ = 0
    #for i in range(len(values)):
    #    if(currValueIndex == i):
    #        jacobianMatrix = values[currValueIndex] * (1 - values[currValueIndex])
    #    else:
    #        jacobianMatrix = -1 * values[currValueIndex] * values[i]
    #    summ += lossDerivative(values[i], trueValue[i], len(values)) * jacobianMatrix
    #return summ

    """
    Applies softmax derivative activation function.

    Args:
        trueValue (ndarray): True labels for the input.
        values (ndarray): Predicted softmax output array.
    
    Returns:
        ndarray: Array with softmax derivative applied to it.    
    
    Note:
        this library forces cross entropy if softmax is used so it simplifies to: values - trueValue
    """
    return values - trueValue #the simplification is due to cross entropy and softmax being used at the same time which is forced by library
