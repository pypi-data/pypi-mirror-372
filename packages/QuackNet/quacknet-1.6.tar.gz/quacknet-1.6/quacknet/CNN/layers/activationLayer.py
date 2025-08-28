from quacknet.core.activations.activationDerivativeFunctions import ReLUDerivative
import numpy as np

class ActivationLayer: # basically aplies an activation function over the whole Tensor (eg. leaky relu)
    def forward(self, inputTensor):
        """
        Applies the Leaky ReLU activation function to the input tensor.

        Args:
            inputTensor (ndarray): A 3D array representing the input.
        
        Returns:
            ndarray: A tensor with the same shape as the input with Leaky ReLU applied to it.
        """
        alpha = 0.01
        return np.maximum(inputTensor, inputTensor * alpha)

    def _backpropagation(self, errorPatch, inputTensor):
        """
        Compute the gradient of the loss with respect to the input of the activation layer during backpropagation.

        Args:
            errorPatch (ndarray): Error gradient from the next layer.
            inputTensor (ndarray): Input to the activation layer during forward propagation.
        
        Returns:
            inputGradient (ndarray): Gradient of the loss with respect to the inputTensor
        """  
        return errorPatch * ReLUDerivative(inputTensor)
    