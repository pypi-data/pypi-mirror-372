import numpy as np
from quacknet.core.utilities.checker import globalChecker

class RNNBackProp:
    def _Stacked_BPTT(self, inputs, AllHiddenStates, hiddenPreActivationValues, outputPreActivation, targets, outputs):
        self._checkParams(inputs, AllHiddenStates, hiddenPreActivationValues, outputPreActivation, targets, outputs)
        
        inputWeightGradients = [np.zeros_like(w) for w in self.inputWeights]
        hiddenStateWeightGradients = np.zeros_like(self.hiddenWeights)
        biasGradients = np.zeros_like(self.biases)

        outputWeightGradients = np.zeros((self.outputSize, self.hiddenSizes[-1]))
        outputbiasGradients = np.zeros(self.outputSize)
        
        T = len(inputs) # number of time steps
        L = len(self.hiddenSizes) # number of hidden layers
        batchSize = inputs[0].shape[0]

        outputLoss = self.lossDerivative(outputs, targets, batchSize*T*outputs.shape[1])

        outputActivationDeriv = self.activationDerivative(outputPreActivation)
        outputLoss = outputLoss * outputActivationDeriv

        lastHidden = AllHiddenStates[-1][-1]

        outputWeightGradients += np.sum(outputLoss.T @ lastHidden, axis=0, keepdims=True)  
        outputbiasGradients += np.sum(outputLoss, axis=0)

        delta = []
        for l in range(L):
            delta.append(np.zeros((batchSize, self.hiddenSizes[l])))

        delta[L - 1] = np.dot(outputLoss, self.outputWeight)

        for t in reversed(range(T)):
            for l in reversed(range(L)):
                preAct = hiddenPreActivationValues[t][l]
                actDeriv = self.activationDerivative(preAct)

                error = delta[l] * actDeriv
                
                inputToLayer = inputs[t]
                if(l != 0):
                    inputToLayer = AllHiddenStates[t][l - 1]

                inputWeightGradients[l] += np.dot(error.T, inputToLayer)
                biasGradients[l] += np.sum(error.T, axis=1, keepdims=True)
                
                if t > 0:
                    hiddenStateWeightGradients[l] += np.dot(error.T, AllHiddenStates[t - 1][l]) 

                if t > 0:
                    delta[l] = np.dot(error, self.hiddenWeights[l])  
                    if l > 0:
                        delta[l - 1] += np.dot(error, self.inputWeights[l]) 
                else:
                    delta[l] = np.zeros_like(delta[l])

        return inputWeightGradients, hiddenStateWeightGradients, biasGradients, outputWeightGradients, outputbiasGradients

    def _checkParams(self, inputs, AllHiddenStates, preActivationValues, outputPreActivation, targets, outputs):
        if(globalChecker.enabled == True):
            batchSize, T, inputSize = inputs.shape
            L = len(self.hiddenSizes)

            globalChecker.checkEqual(T, len(AllHiddenStates), f"Sequence length {T} must match hidden states length {len(AllHiddenStates)}")
            globalChecker.checkEqual(T, len(preActivationValues), f"Sequence length {T} must match pre-activation values length {len(preActivationValues)}")

            for t in range(T):
                currentInput = inputs[:, t, :]
                globalChecker.checkSize(currentInput.ndim, 2, f"Input at time {t} must be 2D (batchSize, inputSize)")
                globalChecker.checkShape(currentInput.shape, (batchSize, self.inputSize), f"Input at time {t} has shape {currentInput.shape} but expected ({batchSize}, {self.inputSize})")

                globalChecker.checkSize(len(AllHiddenStates[t]), L, f"Expected {L} hidden layers at time {t}, got {len(AllHiddenStates[t])}")
                globalChecker.checkSize(len(preActivationValues[t]), L, f"Expected {L} pre-activations at time {t}, got {len(preActivationValues[t])}")

                for l in range(L):
                    expectedShape = (batchSize, self.hiddenSizes[l])
                    globalChecker.checkShape(AllHiddenStates[t][l].shape, expectedShape, f"Hidden state at time {t}, layer {l} has shape {AllHiddenStates[t][l].shape}, expected {expectedShape}")
                    globalChecker.checkShape(preActivationValues[t][l].shape, expectedShape, f"Pre-activation at time {t}, layer {l} has shape {preActivationValues[t][l].shape}, expected {expectedShape}")

            globalChecker.checkShape(outputPreActivation.shape, (batchSize, self.outputSize), f"Output pre-activation shape {outputPreActivation.shape} expected {(batchSize, self.outputSize)}")
            globalChecker.checkShape(targets.shape, (batchSize, self.outputSize), f"Targets shape {targets.shape} does not match expected {(batchSize, self.outputSize)}")
            globalChecker.checkShape(outputs.shape, (batchSize, self.outputSize), f"Output has shape {outputs.shape} but expected ({batchSize}, {self.outputSize})")

            for l in range(L):
                inputShape = (self.hiddenSizes[l], self.inputSize if l == 0 else self.hiddenSizes[l - 1])
                hiddenShape = (self.hiddenSizes[l], self.hiddenSizes[l])
                biasShape = (self.hiddenSizes[l], 1)

                globalChecker.checkShape(self.inputWeights[l].shape, inputShape, f"Input weight at layer {l} has shape {self.inputWeights[l].shape}, expected {inputShape}")
                globalChecker.checkShape(self.hiddenWeights[l].shape, hiddenShape, f"Hidden weight at layer {l} has shape {self.hiddenWeights[l].shape}, expected {hiddenShape}")
                globalChecker.checkShape(self.biases[l].shape, biasShape, f"Bias at layer {l} has shape {self.biases[l].shape}, expected {biasShape}")

            globalChecker.checkShape(self.outputWeight.shape, (self.outputSize, self.hiddenSizes[-1]), f"Output weight shape {self.outputWeight.shape}, expected ({self.outputSize}, {self.hiddenSizes[-1]})")
            globalChecker.checkShape(self.outputBias.shape, (self.outputSize, 1), f"Output bias shape {self.outputBias.shape}, expected ({self.outputSize}, 1)")