import numpy as np

class EmbeddingLayer:
    def __init__(self, vocabSize, embedDimension):
        self.vocabSize = vocabSize #number of unique tokens 
        self.embedDimension = embedDimension
        self.weights = np.random.randn(vocabSize, embedDimension) * 0.01

    def forwardPropagation(self, input):
        self.input = input
        return self.weights[input]
    
    def backwardPropagation(self, outputGradient):
        gradients = np.zeros_like(self.weights)
        if(self.input.ndim == 1):
            for seq in range(self.input.shape[0]):
                idx = self.input[seq]
                gradients[idx] += outputGradient[0, seq]
        elif(self.input.ndim == 2):
            for b in range(self.input.shape[0]):
                for seq in range(self.input.shape[1]):
                    idx = self.input[b, seq]
                    gradients[idx] += outputGradient[b, seq]
        else:
            raise ValueError(f"Unexpected input dimension {self.input.ndim}D")
        return gradients