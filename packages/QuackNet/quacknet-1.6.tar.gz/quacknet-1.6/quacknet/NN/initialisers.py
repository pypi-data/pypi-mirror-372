import math
import numpy as np
from quacknet.core.activations.activationFunctions import relu, sigmoid

class Initialisers: 
    def createWeightsAndBiases(self):
        #weights are in [number of layers][size of current layer][size of next layer]
        for i in range(1, len(self.layers)):
            currSize = self.layers[i][0]
            lastSize = self.layers[i - 1][0]
            actFunc = self.layers[i][1]

            if(actFunc == relu):
                bounds =  math.sqrt(2 / lastSize) # He initialisation
            elif(actFunc == sigmoid):
                bounds = math.sqrt(6/ (lastSize + currSize)) # Xavier initialisation
            else:
                bounds = 1
                
            self.weights.append(np.random.normal(0, bounds, size=(lastSize, currSize)))
            self.biases.append(np.random.normal(0, bounds, size=(currSize)))
        