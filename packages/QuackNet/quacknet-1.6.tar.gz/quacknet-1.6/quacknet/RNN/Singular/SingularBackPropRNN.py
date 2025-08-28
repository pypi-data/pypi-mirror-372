import numpy as np
from quacknet.core.utilities.checker import globalChecker

class RNNBackProp:
    def _Singular_BPTT(self, inputs, AllHiddenStates, hiddenPreActivationValues, outputPreActivation, targets, outputs):
        self._checkParams(inputs, AllHiddenStates, hiddenPreActivationValues, outputPreActivation, targets, outputs)
        
        batchSize, sequenceLength, inputSize = inputs.shape
        
        inputWeightGradients = np.zeros_like(self.inputWeight)
        hiddenStateWeightGradients = np.zeros_like(self.hiddenWeight)
        biasGradients = np.zeros_like(self.bias)
        outputWeightGradients = np.zeros((self.outputSize, self.hiddenSize))
        outputbiasGradients = np.zeros(self.outputSize)

        delta = np.zeros((batchSize, self.hiddenSize, 1))

        outputLoss = self.lossDerivative(outputs, targets, batchSize)
        outputActivationDeriv = self.activationDerivative(outputPreActivation)
        outputLoss = outputLoss * outputActivationDeriv

        lastHidden = AllHiddenStates[-1]
        outputWeightGradients += np.sum(np.matmul(outputLoss, np.transpose(lastHidden, (0, 2, 1))), axis=0)
        outputbiasGradients += np.sum(outputLoss, axis=(0, 1))

        for i in reversed(range(sequenceLength)):
            hiddenPreAct = hiddenPreActivationValues[i] 
            hiddenDeriv = self.activationDerivative(hiddenPreAct) 

            outputLossBackprop = np.matmul(np.transpose(self.outputWeight)[None, :, :], outputLoss)  # (B, hiddenSize, 1)
            error = (outputLossBackprop + delta) * hiddenDeriv 

            inputWeightGradients += np.sum(np.matmul(error, inputs[:, i, :][:, None, :]), axis=0)
            biasGradients += np.sum(error, axis=0)

            if i > 0:
                prevHidden = AllHiddenStates[i - 1] 
                hiddenStateWeightGradients += np.sum(np.matmul(error, np.transpose(prevHidden, (0, 2, 1))), axis=0)

            delta = np.matmul(np.transpose(self.hiddenWeight)[None, :, :], error)

            outputLoss = np.zeros_like(outputLoss)

        return inputWeightGradients, hiddenStateWeightGradients, biasGradients, outputWeightGradients, outputbiasGradients

    def _checkParams(self, inputs, AllHiddenStates, preActivationValues, outputPreActivation, targets, outputs):
        if globalChecker.enabled:
            inputs = np.array(inputs)
            batchSize, T, inputSize = inputs.shape

            globalChecker.checkTrue(T == len(AllHiddenStates), "Mismatch in sequence length between inputs and hidden states")
            globalChecker.checkTrue(T == len(preActivationValues), "Mismatch in sequence length between inputs and pre-activations")
            globalChecker.checkTrue(inputSize == self.inputSize, f"Expected inputSize {self.inputSize}, got {inputSize}")

            for t in range(T):
                globalChecker.checkShape(inputs[:, t, :].shape, (batchSize, self.inputSize), f"inputs[:, {t}, :] has shape {inputs[:, t, :].shape}, expected ({batchSize}, {self.inputSize})")
                globalChecker.checkShape(AllHiddenStates[t].shape, (batchSize, self.hiddenSize, 1), f"hiddenStates[{t}] has shape {AllHiddenStates[t].shape}, expected ({batchSize}, {self.hiddenSize}, 1)")
                globalChecker.checkShape(preActivationValues[t].shape, (batchSize, self.hiddenSize, 1), f"preActivation[{t}] has shape {preActivationValues[t].shape}, expected ({batchSize}, {self.hiddenSize}, 1)")

            globalChecker.checkShape(outputPreActivation.shape, (batchSize, self.outputSize, 1), f"outputPreActivation has shape {outputPreActivation.shape}, expected ({batchSize}, {self.outputSize}, 1)")
            globalChecker.checkShape(targets.shape, (batchSize, self.outputSize, 1), f"targets has shape {targets.shape}, expected ({batchSize}, {self.outputSize}, 1)")
            globalChecker.checkShape(outputs.shape, (batchSize, self.outputSize, 1), f"outputs has shape {outputs.shape}, expected ({batchSize}, {self.outputSize}, 1)")

            globalChecker.checkShape(self.inputWeight.shape, (self.hiddenSize, self.inputSize), f"inputWeight shape is {self.inputWeight.shape}, expected ({self.hiddenSize}, {self.inputSize})")
            globalChecker.checkShape(self.hiddenWeight.shape, (self.hiddenSize, self.hiddenSize), f"hiddenWeight shape is {self.hiddenWeight.shape}, expected ({self.hiddenSize}, {self.hiddenSize})")
            globalChecker.checkShape(self.outputWeight.shape, (self.outputSize, self.hiddenSize), f"outputWeight shape is {self.outputWeight.shape}, expected ({self.outputSize}, {self.hiddenSize})")
            globalChecker.checkShape(self.bias.shape, (self.hiddenSize, 1), f"bias shape is {self.bias.shape}, expected ({self.hiddenSize}, 1)")
            globalChecker.checkShape(self.outputBias.shape, (self.outputSize, 1), f"outputBias shape is {self.outputBias.shape}, expected ({self.outputSize}, 1)")