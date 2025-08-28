import numpy as np

class DenseLayer: # basically a fancy neural network
    def __init__(self, NeuralNetworkClass):
        """
        Initialises a dense layer using a NeuralNetworkClass.

        Args:
            NeuralNetworkClass (class): the fully connected neural network class.
        """
        self.NeuralNetworkClass = NeuralNetworkClass
        self.orignalShape = 0   # orignalShape is the original shape of the input tensor
        
    def _flatternTensor(self, inputTensor):
        """
        Flattens a tensor into a 1D array.

        Args:
            inputTensor (ndarray): A tensor of any shape.
        
        Returns:
            ndarray: A 1D array containing every element of the input tensor.
        """
        inputTensor = np.array(inputTensor)
        batchSize = inputTensor.shape[0]
        return inputTensor.reshape(batchSize, -1)

    def forward(self, inputTensor):
        """
        Flattens the input tensor and performs a forward pass.

        Args:
            inputTensor (ndarray): Input tensor to flatten and process.
        
        Returns:
            ndarray: Output of the dense layer.
        """
        self.orignalShape = np.array(inputTensor).shape
        inputArray = self._flatternTensor(inputTensor)
        self.layerNodes = self.NeuralNetworkClass.forwardPropagation(inputArray)
        return self.layerNodes[-1]
    
    def _backpropagation(self, trueValues): #return weigtGradients, biasGradients, errorTerms
        """
        Performs backpropagation through the dense layer.

        Args:
            trueValues (ndarray): True labels for the input data.
        
        Returns:
            weightGradients (list of ndarray): Gradients of weights for each layer.
            biasGradients (list of ndarray): Gradients of biases for each layer.
            errorTerms (ndarray): Error terms from the output layer weights, reshaped to the input tensor.   
        """  
        weightGradients, biasGradients, errorTerms = self.NeuralNetworkClass._backPropgation(
            self.layerNodes, 
            trueValues,
            True
        )
        #errorTerms = np.array(self.NeuralNetworkClass.weights).T @ errorTerms 
        #errorTerms = errorTerms.reshape(self.orignalShape)

        for i in reversed(range(len(self.NeuralNetworkClass.weights))):
            errorTerms = self.NeuralNetworkClass.weights[i] @ errorTerms.T
            errorTerms = errorTerms.T
        errorTerms = errorTerms.reshape(self.orignalShape)

        return weightGradients, biasGradients, errorTerms