from quacknet.core.activations.activationFunctions import relu, sigmoid, linear, tanH, softMax
from quacknet.RNN.Singular.SingularBackPropRNN import RNNBackProp
from quacknet.core.losses.lossFunctions import MAELossFunction, MSELossFunction, CrossEntropyLossFunction
from quacknet.core.losses.lossDerivativeFunctions import MAEDerivative, MSEDerivative, CrossEntropyLossDerivative
from quacknet.core.activations.activationDerivativeFunctions import ReLUDerivative, SigmoidDerivative, LinearDerivative, TanHDerivative, SoftMaxDerivative
from quacknet.core.optimisers.adam import Adam
import numpy as np
import math

"""
Singular RNN only has 1 hidden state

InputData --> Hidden State --> Dense Layer (output layer)
"""

class SingularRNN(RNNBackProp): 
    def __init__(self, hiddenStateActivationFunction, outputLayerActivationFunction, lossFunction, useBatches = False, batchSize = 64):
        """
        Initializes the RNN model by setting activation functions, loss function,
        batching options, and creating the Adam optimizer instance.

        Args:
            hiddenStateActivationFunction (str): Name of activation function for hidden states (e.g., "relu", "sigmoid").
            outputLayerActivationFunction (str): Name of activation function for output layer.
            lossFunction (str): Name of the loss function to use (e.g., "mse", "mae", "cross entropy").
            useBatches (bool, optional): Whether to use batching during training. Default is False.
            batchSize (int, optional): Batch size if batching is enabled. Default is 64. 
        """
        self.inputWeight = None
        self.hiddenWeight = None
        self.bias = None
        self.outputWeight = None
        self.outputBias = None
        self.hiddenState = None
        
        funcs = {
            "relu": relu,
            "sigmoid": sigmoid,
            "linear": linear,
            "tanh": tanH,
            "softmax": softMax,
        }
        if(hiddenStateActivationFunction.lower() not in funcs):
            raise ValueError(f"Activation function not made: {hiddenStateActivationFunction.lower()}")
        if(outputLayerActivationFunction.lower() not in funcs):
            raise ValueError(f"Activation function not made: {outputLayerActivationFunction.lower()}")
        self.hiddenStateActivationFunction = funcs[hiddenStateActivationFunction.lower()]
        self.outputLayerActivationFunction = funcs[outputLayerActivationFunction.lower()]

        derivs = {
            relu: ReLUDerivative,
            sigmoid: SigmoidDerivative,
            linear: LinearDerivative,
            tanH: TanHDerivative,
            softMax: SoftMaxDerivative,
        }
        self.activationDerivative = derivs[self.hiddenStateActivationFunction]
        self.outputLayerDerivative = derivs[self.outputLayerActivationFunction]

        lossFunctionDict = {
            "mse": MSELossFunction,
            "mae": MAELossFunction,
            "cross entropy": CrossEntropyLossFunction,"cross": CrossEntropyLossFunction,
        }
        self.lossFunction = lossFunctionDict[lossFunction.lower()]
        lossDerivs = {
            MSELossFunction: MSEDerivative,
            MAELossFunction: MAEDerivative,
            CrossEntropyLossFunction: CrossEntropyLossDerivative,
        }
        self.lossDerivative = lossDerivs[self.lossFunction]

        self.useBatches = useBatches
        self.batchSize = batchSize

        self.adam = Adam(self.forwardSequence, self.backwardPropagation, giveInputsToBackprop=True)

    def forwardSequence(self, inputData): # goes through the whole sequence / time steps
        batchSize, sequenceLegth, _ = inputData.shape
        
        preActivations = []
        allHiddenStates = []

        for i in range(sequenceLegth):
            xi = inputData[:, i, :].reshape(batchSize, -1, 1)
            preAct, outputPreAct, output = self._oneStep(xi)
            preActivations.append(preAct)
            allHiddenStates.append(self.hiddenState.copy())
        self.preActivations = preActivations
        self.allHiddenStates = allHiddenStates
        self.outputPreAct = outputPreAct
        return output

    def _oneStep(self, inputData): # forward prop on 1 time step
        preActivation, self.hiddenState = self._calculateHiddenLayer(inputData, self.hiddenState, self.inputWeight, self.hiddenWeight, self.bias, self.hiddenStateActivationFunction)
        preAct, output = self._calculateOutputLayer(self.hiddenState, self.outputWeight, self.outputBias, self.outputLayerActivationFunction)
        return preActivation, preAct, output

    def _calculateHiddenLayer(self, inputData, lastHiddenState, inputWeight, hiddenWeight, bias, activationFunction): # a( w_x * x + w_h * h + b )
        weighttedInp = np.matmul(inputWeight, inputData)
        weightedHidden = np.matmul(hiddenWeight, lastHiddenState)
        biasBrodcast = bias.reshape(1, -1, 1)
        preActivation = weighttedInp + weightedHidden + biasBrodcast
        newHiddenState = activationFunction(preActivation)
        return preActivation, newHiddenState

    def _calculateOutputLayer(self, input, outputWeight, outputBias, activationFunction): # a( w_o * o + b_o)
        weigthedOutput = np.matmul(outputWeight, input)
        outputBiasBrodcast = outputBias.reshape(1, -1, 1)
        preActivation = weigthedOutput + outputBiasBrodcast
        output = activationFunction(preActivation)
        return preActivation, output

    def _initialiseWeights(self, outputSize, inputSize, activationFunction):
        if(activationFunction == relu):
            bounds = math.sqrt(2 / inputSize) # He initialisation
        elif(activationFunction == sigmoid):
            bounds = math.sqrt(6 / (inputSize + outputSize)) # Xavier initialisation
        else:
            bounds = 1 / np.sqrt(inputSize) # default
        w = np.random.normal(0, bounds, size=(outputSize, inputSize))
        return w
    
    def initialiseWeights(self, inputSize, hiddenSize, outputSize):
        """
        Initializes weights and biases for input, hidden, and output layers,
        and sets initial hidden state.

        Args:
            inputSize (int): Size of the input feature vector.
            hiddenSize (int): Number of units in the hidden layer.
            outputSize (int): Size of the output vector.
        """
        self.inputWeight = self._initialiseWeights(hiddenSize, inputSize, self.hiddenStateActivationFunction)
        self.hiddenWeight = self._initialiseWeights(hiddenSize, hiddenSize, self.hiddenStateActivationFunction)
        self.outputWeight = self._initialiseWeights(outputSize, hiddenSize, self.outputLayerActivationFunction)
        self.bias = np.zeros((hiddenSize, 1))
        self.outputBias = np.zeros((outputSize, 1))
        self.hiddenState = np.zeros((hiddenSize, 1))
        self.inputSize = inputSize
        self.hiddenSize = hiddenSize
        self.outputSize = outputSize

    def backwardPropagation(self, inputs, outputs, targets):
        inputWeightGradients, hiddenStateWeightGradients, biasGradients, outputWeightGradients, outputbiasGradients = self._Singular_BPTT(inputs, self.allHiddenStates, self.preActivations, self.outputPreAct, targets, outputs)
        Parameters =  {
            "I_W": self.inputWeight,
            "b": self.bias,
            "H_W": self.hiddenWeight,
            "O_W": self.outputWeight,
            "O_b": self.outputBias,
        }
  
        Gradients =  {
            "I_W": inputWeightGradients,
            "b": biasGradients,
            "H_W": hiddenStateWeightGradients,
            "O_W": outputWeightGradients,
            "O_b": outputbiasGradients,
        }
        return Parameters, Gradients 

    def optimiser(self, inputData, labels, alpha, beta1, beta2, epsilon):
        AllOutputs, Parameters = self.adam.optimiser(inputData, labels, self.useBatches, self.batchSize, alpha, beta1, beta2, epsilon)
        self.inputWeights = Parameters["I_W"]
        self.biases = Parameters["b"]
        self.hiddenWeights = Parameters["H_W"]
        self.outputWeight = Parameters["O_W"]
        self.outputBias = Parameters["O_b"]
        return AllOutputs

    def train(self, inputData, labels, alpha = 0.001, beta1 = 0.9, beta2 = 0.999, epsilon = 1e-8):
        """
        Trains the model on the given input sequences and labels using the Adam optimizer,
        then calculates and returns the loss.

        Args:
            inputData (ndarray): 3D array of input data with shape (batchSize, sequenceLength, inputSize).
            labels (ndarray): True labels corresponding to the input data.
            alpha (float, optional): Learning rate for the optimizer. Default is 0.001.
            beta1 (float, optional): Beta1 parameter for Adam optimizer. Default is 0.9.
            beta2 (float, optional): Beta2 parameter for Adam optimizer. Default is 0.999.
            epsilon (float, optional): Epsilon parameter for Adam optimizer to prevent division by zero. Default is 1e-8.

        Returns:
            float: Calculated loss between model outputs and true labels.
        """
        assert np.array(inputData).ndim == 3, f"Dimension wrong size, got {np.array(inputData).ndim}, expected 3"
        AllOutputs = self.optimiser(inputData, labels, alpha, beta1, beta2, epsilon)
        AllOutputs = np.reshape(AllOutputs, (np.array(labels).shape))
        loss = self.lossFunction(AllOutputs, labels)
        return loss