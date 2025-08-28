import numpy as np
import math

class Conv1DLayer():
    def __init__(self, kernalSize, depth, numKernals, stride, padding = "no"):
        self.kernalSize = kernalSize
        self.numKernals = numKernals
        self.kernalWeights = []
        self.kernalBiases = []
        self.depth = depth
        self.stride = stride
        self.padding = padding

        # cant do padding.lower() because if user puts 1 it will throw a error
        if(padding == "no" or padding == "n" or padding == "NO" or padding == "N"):
            self.usePadding = False
        else:
            self.padding = int(self.padding)
            self.usePadding = True
    
    def _padImage(self, inputTensor, kernalSize, strideLength, typeOfPadding): #pads image
        batch_size, depth, length = inputTensor.shape
        paddingSize = math.ceil(((strideLength - 1) * length - strideLength + kernalSize) / 2)
        padded_length = length + 2 * paddingSize
        
        padded = np.full((batch_size, depth, padded_length), typeOfPadding)
        
        for b in range(batch_size):
            for d in range(depth):
                padded[b, d, paddingSize:paddingSize + length] = inputTensor[b, d]
        return padded

    def forward(self, inputTensor):
        if(self.usePadding == True):
            inputTensor = self._padImage(inputTensor, self.kernalSize, self.stride, self.padding)

        batchSize, depth, seqLength = inputTensor.shape
        outputLength = (seqLength - self.kernalSize) // self.stride + 1
        output = np.zeros((batchSize, self.numKernals, outputLength))
        
        for b in range(batchSize):
            for k in range(self.numKernals):
                kernal = self.kernalWeights[k]
                bias = self.kernalBiases[k]
                for i in range(outputLength):
                    start = i * self.stride
                    end = start + self.kernalSize
                    region = inputTensor[b, :, start: end]

                    if(region.shape != kernal.shape):
                        continue

                    output[b, k, i] = np.sum(region * kernal) + bias
        return output
                    
    def _backpropagation(self, errorPatch, inputTensor): 
        if(self.usePadding == True):
            inputTensor = self._padImage(inputTensor, self.kernalSize, self.stride, self.padding)
        
        batchSize, depth, seqLength = inputTensor.shape
        _, _, outputLength = errorPatch.shape

        weightGradients = np.zeros_like(self.kernalWeights)
        inputErrorTerms = np.zeros_like(inputTensor)

        for b in range(batchSize):
            for k in range(self.numKernals):
                for d in range(self.depth):
                    for i in range(outputLength):
                        start = i * self.stride
                        end = start + self.kernalSize
                        if(end > seqLength):
                            continue
                        region = inputTensor[b, d, start: end]
                        weightGradients[k, d] += errorPatch[b, k, i] * region
        
        biasGradients = np.sum(errorPatch, axis = (0, 2))

        flippedKernels = self.kernalWeights[:, :, ::-1]
        for b in range(batchSize):
            for k in range(self.numKernals):
                for d in range(self.depth):
                    for i in range(outputLength):
                        start = i * self.stride
                        end = start + self.kernalSize
                        if(end > seqLength):
                            continue
                        inputErrorTerms[b, d, start: end] += errorPatch[b, k, i] * flippedKernels[k, d]
                
        return weightGradients, biasGradients, inputErrorTerms