from quacknet.core.activations.activationFunctions import relu, sigmoid, tanH, linear, softMax
from quacknet.core.activations.activationDerivativeFunctions import ReLUDerivative, SigmoidDerivative, TanHDerivative, LinearDerivative, SoftMaxDerivative
from quacknet.core.losses.lossDerivativeFunctions import MSEDerivative, MAEDerivative, CrossEntropyLossDerivative
from quacknet.core.losses.lossFunctions import MSELossFunction, MAELossFunction, CrossEntropyLossFunction
import numpy as np

'''
output layer backpropogation for weights:
e = (dL/da) * f'(z)
e = error term
dL/da = derivative of the loss function
f'() = derivative of the activation function
z = the current layer's node (only one)

(dL/dW) = e * a
dL/dW  = derivative of loss function with respect to weight
e = error term
a = past layer's node value

nw = ow - r * (dL/dW)
nw = new weight
ow = old weight
r = learning rate
(dL/dW) = derivative of loss function with respect to weight

hidden layer backpropgation for weights:
e = SUM(e[l + 1][k] * w[l + 1][k]) * f'(z)
e = error term
SUM(e[l + 1][k] * w[l + 1][k]) = the sum of the next layers's error term for the current node multiplied by the weight in the nextlayer connected to the current one
f'() = derivative of the activation function
z = the current layer's node (only one)

(dL/dW) = e * a
dL/dW  = derivative of loss function with respect to weight
e = error term
a = past layer's node value

nw = ow - r * (dL/dW)
nw = new weight
ow = old weight
r = learning rate
(dL/dW) = derivative of loss function with respect to weight
'''

def _outputLayerWeightChange(lossDerivative, activationDerivative, currentLayerNodes, pastLayerNodes, trueValues): 
    """
    Calculate the weight gradients and error terms for the output layer during backpropagation.

    Args:
        lossDerivative (function): Derivative function of the loss function.
        activationDerivative (function): Derivative function of the activation function.
        currentLayerNodes (ndarray): Output values of the current (output) layer.
        pastLayerNodes (ndarray): Output values of the previous layer.
        trueValues (ndarray): True target values for the output.
    
    Returns:
        weightGradients (ndarray): Gradient of the loss with respect to the weight.
        errorTerms (ndarray): Error terms for the output layer nodes.
    """
    if(activationDerivative == SoftMaxDerivative and lossDerivative == CrossEntropyLossDerivative):
        errorTerms = currentLayerNodes - trueValues
    else:
        lossDerivativeValue = lossDerivative(currentLayerNodes, trueValues, len(currentLayerNodes))
        errorTerms = lossDerivativeValue * activationDerivative(currentLayerNodes)
    
    if(pastLayerNodes.ndim == 1):
        weightGradients = np.outer(pastLayerNodes, errorTerms)
    elif(pastLayerNodes.ndim == 2):
        weightGradients = pastLayerNodes.T @ errorTerms
    else:
        raise ValueError(f"Shouldnt be a 3D tensor")

    return weightGradients, errorTerms

def _hiddenLayerWeightChange(pastLayerErrorTerms, pastLayerWeights, activationDerivative, currentLayerNodes, pastLayerNodes):
    """
    Calculate the weight gradients and error terms for the hidden layer during backpropagation.

    Args:
        pastLayerErrorTerms (ndarray): Error terms for the next layer.
        pastLayerWeights (ndarray): Weights connecting current layer to the next layer.
        activationDerivative (function): Derivative function of the activation function for the current layer.
        currentLayerNodes (ndarray): Output values of the current layer.
        pastLayerNodes (ndarray): Output values of the previous layer.
        
    Returns:
        weightGradients (ndarray): Gradient of the loss with respect to the weight.
        errorTerms (ndarray): Error terms for the current layer nodes.
    """   
    errorTerms = (pastLayerErrorTerms @ pastLayerWeights.T) * activationDerivative(currentLayerNodes)
    if(pastLayerNodes.ndim == 1):
        weightGradients = np.outer(pastLayerNodes, errorTerms)
    elif(pastLayerNodes.ndim == 2):
        weightGradients = pastLayerNodes.T @ errorTerms
    else:
        raise ValueError(f"Shouldnt be a 3D tensor")
    
    return weightGradients, errorTerms

def _outputLayerBiasChange(lossDerivative, activationDerivative, currentLayerNodes, trueValues):
    """
    Calculate the bias gradients and error terms for the output layer during backpropagation.

    Args:
        lossDerivative (function): Derivative function of the loss function.
        activationDerivative (function): Derivative function of the activation function.
        currentLayerNodes (ndarray): Output values of the current (output) layer.
        trueValues (ndarray): True target values for the output.
    
    Returns:
        biasGradients (ndarray): Gradient of the loss with respect to the biases.
        errorTerms (ndarray): Error terms for the output layer nodes.
    """
    if(activationDerivative == SoftMaxDerivative and lossDerivative == CrossEntropyLossDerivative):
        errorTerms = currentLayerNodes - trueValues
    else:
        lossDerivativeValue = lossDerivative(currentLayerNodes, trueValues, len(currentLayerNodes))
        errorTerms = lossDerivativeValue * activationDerivative(currentLayerNodes)
    if(currentLayerNodes.ndim == 1):
        biasGradients = errorTerms
    elif(currentLayerNodes.ndim == 2):
        biasGradients = np.mean(errorTerms, axis=0)
    else:
        raise ValueError(f"Shouldnt be a 3D tensor")

    return biasGradients, errorTerms


def _hiddenLayerBiasChange(pastLayerErrorTerms, pastLayerWeights, activationDerivative, currentLayerNodes):
    """
    Calculate the bias gradients and error terms for the hidden layer during backpropagation.

    Args:
        pastLayerErrorTerms (ndarray): Error terms for the next layer.
        pastLayerWeights (ndarray): Weights connecting current layer to the next layer.
        activationDerivative (function): Derivative function of the activation function for the current layer.
        currentLayerNodes (ndarray): Output values of the current layer.
        
    Returns:
        biasGradients (ndarray): Gradient of the loss with respect to the biases.
        errorTerms (ndarray): Error terms for the current layer nodes.
    """  
    errorTerms = (pastLayerErrorTerms @ pastLayerWeights.T) * activationDerivative(currentLayerNodes)
    if(currentLayerNodes.ndim == 1):
        biasGradients = errorTerms
    elif(currentLayerNodes.ndim == 2):
        biasGradients = np.mean(errorTerms, axis=0)
    else:
        raise ValueError(f"Shouldnt be a 3D tensor")

    return biasGradients, errorTerms

def _backPropgation(layerNodes, weights, biases, trueValues, layers, lossFunction, returnErrorTermForCNN = False):
    """
    Perform backpropagation over the network layers to compute gradients for weights and biases.

    Args:
        layerNodes (list of ndarray): List of output values for each layer.
        weights (list of ndarray): List of weights for each layer.
        biases (list of ndarray): List of biases for each layer.
        trueValues (list of ndarray): True target values for the output layer.
        layers (list of tuples): Network layers with format (number of nodes, activation function).
        lossFunction (function): Loss function used.
        returnErrorTermForCNN (bool, optional): Whether to return error terms for CNN backpropagation. Defaults to False.

    Returns:
        weightGradients (list of ndarray): Gradients of weights for each layer.
        biasGradients (list of ndarray): Gradients of biases for each layer.
        If returnErrorTermForCNN is True:
            hiddenWeightErrorTermsForCNNBackpropgation (ndarray): Error terms from the output layer weights.   
    """  
    lossDerivatives = {
        MSELossFunction: MSEDerivative,
        MAELossFunction: MAEDerivative,
        CrossEntropyLossFunction: CrossEntropyLossDerivative,
    }
    activationDerivatives = {
        relu: ReLUDerivative,
        sigmoid: SigmoidDerivative,
        linear: LinearDerivative,
        tanH: TanHDerivative,
        softMax: SoftMaxDerivative,
    }
    w, weightErrorTerms = _outputLayerWeightChange(lossDerivatives[lossFunction], activationDerivatives[layers[len(layers) - 1][1]], layerNodes[len(layerNodes) - 1], layerNodes[len(layerNodes) - 2], trueValues)
    b, biasErrorTerms = _outputLayerBiasChange(lossDerivatives[lossFunction], activationDerivatives[layers[len(layers) - 1][1]], layerNodes[len(layerNodes) - 1], trueValues)
    hiddenWeightErrorTermsForCNNBackpropgation = weightErrorTerms
    weightGradients = [w]
    biasGradients = [b]
    for i in range(len(layers) - 2, 0, -1):
        w, weightErrorTerms = _hiddenLayerWeightChange(
            weightErrorTerms, 
            weights[i], 
            activationDerivatives[layers[i][1]], 
            layerNodes[i], 
            layerNodes[i - 1]
        )
        b, biasErrorTerms = _hiddenLayerBiasChange(
            biasErrorTerms, 
            weights[i], 
            activationDerivatives[layers[i][1]], 
            layerNodes[i]
        )
        weightGradients.append(w)
        biasGradients.append(b)
    weightGradients.reverse()
    biasGradients.reverse()
    if(returnErrorTermForCNN == True):
        return weightGradients, biasGradients, hiddenWeightErrorTermsForCNNBackpropgation
    return weightGradients, biasGradients
