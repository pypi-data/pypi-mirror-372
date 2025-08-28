import numpy as np

class NormLayer:
    def __init__(self, features, epsilon = 1e-6):
        self.gamma = np.ones((1, 1, features)) # scale
        self.beta = np.zeros((1, 1, features)) # shift
        self.epsilon = epsilon # adds a small constant to avoid division by 0
        self.input = None

    def forwardPropagation(self, x):
        self.input = x
        self.mean = np.mean(x, axis=-1, keepdims=True) 
        self.variance = np.var(x, axis=-1, keepdims=True)
        self.std = np.sqrt(self.variance + self.epsilon)
        self.normalised = (x - self.mean) / self.std
        return self.gamma * self.normalised + self.beta
    
    def backwardPropagation(self, outputDerivative):
        m = self.input.shape[-1]

        gammaDerivative = np.sum(outputDerivative * self.normalised, axis=(0, 1), keepdims=True)
        betaDerivative = np.sum(outputDerivative, axis=(0, 1), keepdims=True)

        dx = outputDerivative * self.gamma

        inputDerivative = (1.0 / m) * (1 / self.std) * (
            m * dx 
            - np.sum(dx, axis=-1, keepdims=True) 
            - self.normalised * np.sum(dx * self.normalised, axis=-1, keepdims=True)
        )

        return inputDerivative, gammaDerivative, betaDerivative