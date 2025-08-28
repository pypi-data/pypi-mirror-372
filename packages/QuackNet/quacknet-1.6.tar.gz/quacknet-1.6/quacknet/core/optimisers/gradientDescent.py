import numpy as np

class GD:
    def __init__(self, forwardPropagationFunction, backwardPropagationFunction, giveInputsToBackprop = False):
        self.forwardPropagationFunction = forwardPropagationFunction
        self.backwardPropagationFunction = backwardPropagationFunction
        self.giveInputsToBackprop = giveInputsToBackprop 

    def optimiser(self, inputData, labels, useBatches, batchSize, learningRate):
        return self._trainGradientDescent_Batching(inputData, labels, learningRate)

    def _trainGradientDescent_Batching(self, inputData, labels, learningRate):
        allNodes = []  
        accumulatedGradients = {}
        Parameters = None 
        for i in range(len(inputData)):
            layerNodes = self.forwardPropagationFunction(inputData[i])
            allNodes.append(layerNodes)

            if(self.giveInputsToBackprop == False):
                Parameters, Gradients = self.backwardPropagationFunction(layerNodes, labels[i])
            else:
                Parameters, Gradients = self.backwardPropagationFunction(inputData[i], layerNodes, labels[i])

            for key in Gradients:
                if key not in accumulatedGradients:
                    accumulatedGradients[key] = Gradients[key]
                else:
                    accumulatedGradients[key] += Gradients[key]

        for key in accumulatedGradients:
            if(isinstance(accumulatedGradients[key], list)): # inhomengous array
                for i in range(len(accumulatedGradients[key])):
                    accumulatedGradients[key][i] = np.array(accumulatedGradients[key][i]) / len(inputData)
            else:
                accumulatedGradients[key] = accumulatedGradients[key] / len(inputData)
        
        Parameters = self._updateWeightsBiases(Parameters, accumulatedGradients, learningRate)
        return allNodes, Parameters
    
    def _updateWeightsBiases(self, Parameters, Gradients, learningRate):
        for key in Gradients:
            if(isinstance(Gradients[key], list)): # if the Gradient is a inhomengous list (jagged array, which numpy doesnt like)
                for i in range(len(Gradients[key])):
                    Parameters[key][i] -= learningRate * Gradients[key][i]
            else:
                Parameters[key] -= learningRate * Gradients[key]
        return Parameters