import numpy as np

class LinearLayer:
    def __init__(self, batchSize, sequenceLength, inFeatures, outFeatures):
        self.batchSize = batchSize
        self.sequenceLength = sequenceLength
        self.inFeatures = inFeatures
        self.outFeatures = outFeatures

        self._init_weights()

        self.input = None
        self.output = None
        self.dWeights = None
        self.dBias = None

    def _init_weights(self):
        self.weights = (np.random.randn(self.inFeatures, self.outFeatures) * (1.0 / np.sqrt(max(1, self.inFeatures))))
        self.bias = np.zeros((1, self.outFeatures), dtype=np.float32)

    def forwardPropagation(self, x):
        self.input = x

        B, T, D = self.input.shape
        x_flat = self.input.reshape(-1, D)                   
        out_flat = x_flat @ self.weights + self.bias        
        self.output = out_flat.reshape(B, T, self.outFeatures) 
        return self.output

    def backwardPropagation(self, outputGradient):
        B, T, V = outputGradient.shape

        D = self.inFeatures
        x_flat = self.input.reshape(-1, D)   
        dOut_flat = outputGradient.reshape(-1, V)      

        weightsGrad = x_flat.T @ dOut_flat   
        biasGrad = dOut_flat.sum(axis=0)    

        dx_flat = dOut_flat @ self.weights.T
        inputDerivative = dx_flat.reshape(B, T, D)

        self.dWeights = weightsGrad
        self.dBias = biasGrad

        Parameters =  {
            "LO_W": self.weights,
            "LO_b": self.bias,
        }
  
        Gradients =  {
            "LO_W": weightsGrad,
            "LO_b": biasGrad,
        }

        return Parameters, Gradients

