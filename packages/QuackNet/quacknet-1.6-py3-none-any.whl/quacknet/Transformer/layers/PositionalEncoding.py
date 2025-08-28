import numpy as np

"""
Positional encoding uses sinusoidal positional encoding to encode the position of each element

"""

class PositionalEncoding:
    def __init__(self, maxDimension, embeddingSize):
        self.maxDimension = maxDimension
        self.embeddingSize = embeddingSize
        self.encoding = self.createEmbed()

    def createEmbed(self):
        position = np.arange(self.maxDimension)[:, np.newaxis]
        divTerm = np.exp(np.arange(0, self.embeddingSize, 2) * -(np.log(100000) / self.embeddingSize))

        positionalEmbedding = np.zeros((self.maxDimension, self.embeddingSize))
        positionalEmbedding[:, 0::2] = np.sin(position * divTerm)
        positionalEmbedding[:, 1::2] = np.cos(position * divTerm)
        return positionalEmbedding
    
    def forwardPropagation(self, inputData):
        return inputData + self.encoding[:np.array(inputData).shape[1]]