import numpy as np

"""
This Feed Forward Network (FFN) is a NN which is applied to each token independantly
But it is the same FFN each time (so it has the same weight and bias)

Number of Layers are hardcoded to be 2, to make code easier to follow
Also ReLU is used as the activation function (may allow users to set the activation function, in the future)
"""

class FeedForwardNetwork:
    def __init__(self, inputDimension, hiddenDimension, W1, b1, W2, b2):
        self.inputDimension = inputDimension
        self.hiddenDimension = hiddenDimension
        self.W1 = W1
        self.b1 = b1
        self.W2 = W2
        self.b2 = b2

        self.createWeights()

    def createWeights(self):
        self.W1 = self._initiaseWeight(self.inputDimension, self.hiddenDimension)
        self.W2 = self._initiaseWeight(self.hiddenDimension, self.inputDimension)
        
        self.b1 = np.zeros((1, self.hiddenDimension))
        self.b2 = np.zeros((1, self.inputDimension))

    def _initiaseWeight(self, inputDimension, outputDimension):
        return np.random.rand(inputDimension, outputDimension) * (1 / np.sqrt(inputDimension))
    
    def forwardPropagation(self, inputTokens): 
        self.input = inputTokens
        self.firstLayer = np.matmul(inputTokens, self.W1) + self.b1
        self.activated = np.maximum(0, self.firstLayer) # ReLU
        output = np.matmul(self.activated, self.W2) + self.b2
        return output
    
    def backwardPropagation(self, outputGradient):
        weightGradient2 = np.matmul(self.activated.transpose(0, 2, 1), outputGradient)
        biasGradient2 = np.sum(outputGradient, axis=(0, 1), keepdims=True)

        activatedGradient = np.matmul(outputGradient, self.W2.T)
        firstLayerDerivative = activatedGradient * (self.firstLayer > 0)

        weightGradient1 = np.matmul(self.input.transpose(0, 2, 1), firstLayerDerivative)
        biasGradient1 = np.sum(firstLayerDerivative, axis=(0, 1), keepdims=True)

        inputDerivative = np.matmul(firstLayerDerivative, self.W1.T)

        return inputDerivative, weightGradient1, biasGradient1, weightGradient2, biasGradient2