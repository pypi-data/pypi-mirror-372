import numpy as np

class Adam:
    def __init__(self, forwardPropagationFunction, backwardPropagationFunction, giveInputsToBackprop = False):
        self.firstMoment = {}
        self.secondMoment = {}
        self.t = 0
        self.forwardPropagationFunction = forwardPropagationFunction
        self.backwardPropagationFunction = backwardPropagationFunction
        self.giveInputsToBackprop = giveInputsToBackprop 

    def optimiser(self, inputData, labels, useBatches, batchSize, alpha, beta1=0.9, beta2=0.999, epsilon=1e-8):
        if(useBatches == True):
            return self._AdamsOptimiserWithBatches(inputData, labels, batchSize, alpha, beta1, beta2, epsilon)
        else:
            return self._AdamsOptimiserWithoutBatches(inputData, labels, alpha, beta1, beta2, epsilon)

    def _AdamsOptimiserWithBatches(self, inputData, labels, batchSize, alpha, beta1, beta2, epsilon):     
        AllOutputs = []
        numBatches = len(inputData) // batchSize
        for i in range(numBatches):
            batchData = np.array(inputData[i*batchSize:(i+1)*batchSize])
            batchLabels = np.array(labels[i*batchSize:(i+1)*batchSize])
            Parameters = None

            output = self.forwardPropagationFunction(batchData)
            AllOutputs.append(output)

            if(self.giveInputsToBackprop == False):
                Parameters, Gradients = self.backwardPropagationFunction(output, batchLabels)
            else:
                Parameters, Gradients = self.backwardPropagationFunction(batchData, output, batchLabels)

            for key in Gradients:
                if(isinstance(Gradients[key], list)): # inhomengous array
                    for j in range(len(Gradients[key])):
                        Gradients[key][j] = np.array(Gradients[key][j]) / batchSize
                else:
                    Gradients[key] = Gradients[key] / batchSize

            Parameters = self._Adams(Parameters, Gradients, alpha, beta1, beta2, epsilon)
        return AllOutputs, Parameters

    def _AdamsOptimiserWithoutBatches(self, inputData, labels, alpha, beta1, beta2, epsilon):   
        AllOutputs = []
        for i in range(len(inputData)):
            input = np.array([inputData[i]])
            lab = np.array([labels[i]])
            output = self.forwardPropagationFunction(input)
            AllOutputs.append(output)

            if(self.giveInputsToBackprop == False):
                Parameters, Gradients = self.backwardPropagationFunction(output, lab)
            else:
                Parameters, Gradients = self.backwardPropagationFunction(input, output, lab)

            Parameters = self._Adams(Parameters, Gradients, alpha, beta1, beta2, epsilon)
        return AllOutputs, Parameters

    def _Adams(self, Parameters, Gradients, alpha, beta1, beta2, epsilon):
        self.t += 1
        for key in Gradients:
            if(isinstance(Gradients[key], list)): # if the Gradient is a inhomengous list (jagged array, which numpy doesnt like)
                for i, grad in enumerate(Gradients[key]):
                    grad = np.array(grad)

                    if key not in self.firstMoment:
                        self.firstMoment[key] = [np.zeros_like(g) for g in Gradients[key]]
                        self.secondMoment[key] = [np.zeros_like(g) for g in Gradients[key]]
                        
                    self.firstMoment[key][i] = beta1 * self.firstMoment[key][i] + (1 - beta1) * grad
                    self.secondMoment[key][i] = beta2 * self.secondMoment[key][i] + (1 - beta2) * (grad ** 2)

                    firstMomentWeightHat = self.firstMoment[key][i] / (1 - beta1 ** self.t)
                    secondMomentWeightHat = self.secondMoment[key][i] / (1 - beta2 ** self.t)

                    Parameters[key][i] -= alpha * firstMomentWeightHat / (np.sqrt(secondMomentWeightHat) + epsilon)
            else:
                if key not in self.firstMoment:
                    self.firstMoment[key] = np.zeros_like(Gradients[key])
                    self.secondMoment[key] = np.zeros_like(Gradients[key])
                        
                self.firstMoment[key] = beta1 * self.firstMoment[key] + (1 - beta1) * Gradients[key]
                self.secondMoment[key] = beta2 * self.secondMoment[key] + (1 - beta2) * (Gradients[key] ** 2)

                firstMomentWeightHat = self.firstMoment[key] / (1 - beta1 ** self.t)
                secondMomentWeightHat = self.secondMoment[key] / (1 - beta2 ** self.t)

                Parameters[key] -= alpha * firstMomentWeightHat / (np.sqrt(secondMomentWeightHat) + epsilon)
        return Parameters
    