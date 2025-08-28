import numpy as np

class SGD:
    def __init__(self, forwardPropagationFunction, backwardPropagationFunction, giveInputsToBackprop = False):
        self.forwardPropagationFunction = forwardPropagationFunction
        self.backwardPropagationFunction = backwardPropagationFunction
        self.giveInputsToBackprop = giveInputsToBackprop 

    def optimiser(self, inputData, labels, useBatches, batchSize, learningRate):
        if(useBatches == True):
            return self._trainStochasticGradientDescent_Batches(inputData, labels, batchSize, learningRate)
        else:
            return self._trainStochasticGradientDescent_WithoutBatches(inputData, labels, learningRate)

    def _trainStochasticGradientDescent_WithoutBatches(self, inputData, labels, learningRate):
        allNodes = []   
        for data in range(len(inputData)):
            layerNodes = self.forwardPropagationFunction(inputData[data])
            allNodes.append(layerNodes)

            if(self.giveInputsToBackprop == False):
                Parameters, Gradients = self.backwardPropagationFunction(layerNodes, labels[data])
            else:
                Parameters, Gradients = self.backwardPropagationFunction(inputData[data], layerNodes, labels[data])

            Parameters = self._updateWeightsBiases(Parameters, Gradients, learningRate)
        return allNodes, Parameters

    def _trainStochasticGradientDescent_Batches(self, inputData, labels, batchSize, learningRate):
        allNodes = []   
        for i in range(0, len(inputData), batchSize):
            batchData = inputData[i:i+batchSize]
            batchLabels = labels[i:i+batchSize]
            acculumalatedGradients = {}
            Parameters = None
            for j in range(len(batchData)):
                layerNodes = self.forwardPropagationFunction(batchData[j])
                allNodes.append(layerNodes)

                if(self.giveInputsToBackprop == False):
                    Parameters, Gradients = self.backwardPropagationFunction(layerNodes, batchLabels[j])
                else:
                    Parameters, Gradients = self.backwardPropagationFunction(batchData[j], layerNodes, batchLabels[j])

                for key in Gradients:
                    if key not in acculumalatedGradients:
                        acculumalatedGradients[key] = Gradients[key]
                    else:
                        acculumalatedGradients[key] += Gradients[key]
            
            for key in acculumalatedGradients:
                if(isinstance(acculumalatedGradients[key], list)): # inhomengous array
                    for i in range(len(acculumalatedGradients[key])):
                        acculumalatedGradients[key][i] = np.array(acculumalatedGradients[key][i]) / batchSize
                else:
                    acculumalatedGradients[key] = acculumalatedGradients[key] / batchSize
            
            Parameters = self._updateWeightsBiases(Parameters, acculumalatedGradients, learningRate)
        return allNodes, Parameters
    
    def _updateWeightsBiases(self, Parameters, Gradients, learningRate):
        for key in Gradients:
            if(isinstance(Gradients[key], list)): # if the Gradient is a inhomengous list (jagged array, which numpy doesnt like)
                for i in range(len(Gradients[key])):
                    Parameters[key][i] -= learningRate * Gradients[key][i]
            else:
                Parameters[key] -= learningRate * Gradients[key]

        return Parameters