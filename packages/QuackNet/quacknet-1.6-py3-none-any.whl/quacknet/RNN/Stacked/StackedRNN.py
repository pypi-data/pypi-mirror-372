from quacknet.core.activations.activationFunctions import relu, sigmoid, linear, tanH, softMax
from quacknet.core.losses.lossFunctions import MAELossFunction, MSELossFunction, CrossEntropyLossFunction
from quacknet.core.losses.lossDerivativeFunctions import MAEDerivative, MSEDerivative, CrossEntropyLossDerivative
from quacknet.core.activations.activationDerivativeFunctions import ReLUDerivative, SigmoidDerivative, LinearDerivative, TanHDerivative, SoftMaxDerivative
from quacknet.RNN.Stacked.StackedBackPropRNN import RNNBackProp
from quacknet.core.optimisers.adam import Adam
import numpy as np
import math

"""
Stacked RNN only has lots of hidden states
InputData --> [ Hidden State Layer 1 --> Hidden State Layer 2 --> ... --> Hidden State Layer N ] --> Dense Layer (output layer)
"""

class StackedRNN(RNNBackProp): 
    def __init__(self, hiddenStateActivationFunction, outputLayerActivationFunction, lossFunction, numberOfHiddenStates, hiddenSizes, useBatches = False, batchSize = 64):
        """
        Initializes the RNN model with specified activation functions, loss function,
        hidden layer configuration, and batching options.

        Args:
            hiddenStateActivationFunction (str): Name of activation function for hidden states (e.g., "relu", "sigmoid").
            outputLayerActivationFunction (str): Name of activation function for output layer.
            lossFunction (str): Name of the loss function to use (e.g., "mse", "mae", "cross entropy").
            numberOfHiddenStates (int): Number of hidden layers in the RNN.
            hiddenSizes (list of int): List specifying the size of each hidden layer.
            useBatches (bool, optional): Whether to use batching during training. Default is False.
            batchSize (int, optional): Batch size if batching is enabled. Default is 64.
        """
        self.inputWeights = None
        self.hiddenWeights = None
        self.biases = None
        self.outputWeight = None
        self.outputBias = None
        self.hiddenStates = None
        
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
        if(useBatches == False):
            self.batchSize = 1
        else:
            self.batchSize = batchSize

        self.numberOfHiddenStates = numberOfHiddenStates
        self.hiddenSizes = hiddenSizes

        assert type(self.hiddenSizes) == list, f"hiddenSizes has to be a list"
        for num in self.hiddenSizes:
            assert isinstance(num, int), f"hiddenSize has to be a list of integers"

        self.adam = Adam(self.forwardSequence, self.backwardPropagation, giveInputsToBackprop=True)

    def forwardSequence(self, inputData): # goes through the whole sequence / time steps
        assert inputData.shape[0] == self.batchSize, f"Input data isnt batched"
        assert inputData.ndim == 3, f"Input data isnt 3D (batchsize, sequenceLength, inputSize)"
        preActivations = []
        allHiddenStates = []
        sequenceLength = inputData.shape[1]
        for i in range(sequenceLength):
            xi = inputData[:, i, :]
            allPreAct, outputPreAct, output, allHidenStates = self._oneStep(xi)
            preActivations.append(allPreAct)
            allHiddenStates.append(allHidenStates)
        self.preActivations = preActivations
        self.allHiddenStates = allHiddenStates
        self.outputPreAct = outputPreAct
        return output

    def _oneStep(self, inputData): # forward prop on 1 time step
        allPreActivations = []
        allHidenStates = []

        currentInput = inputData

        for i in range(self.numberOfHiddenStates):
            preActivation, self.hiddenStates[i] = self._calculateHiddenLayer(currentInput, self.hiddenStates[i], self.inputWeights[i], self.hiddenWeights[i], self.biases[i], self.hiddenStateActivationFunction)
            
            allPreActivations.append(preActivation)
            allHidenStates.append(self.hiddenStates[i])
            currentInput = self.hiddenStates[i]

        preAct, output = self._calculateOutputLayer(allHidenStates[-1], self.outputWeight, self.outputBias, self.outputLayerActivationFunction)
        return allPreActivations, preAct, output.reshape(-1, 1), allHidenStates

    def _calculateHiddenLayer(self, inputData, lastHiddenState, inputWeights, hiddenWeights, bias, activationFunction): # a( w_x * x + w_h * h + b )
        preActivation = np.dot(inputData, inputWeights.T) + np.dot(lastHiddenState, hiddenWeights.T) + bias.T
        newHiddenState = activationFunction(preActivation)
        return preActivation, newHiddenState

    def _calculateOutputLayer(self, input, outputWeight, outputBias, activationFunction): # a( w_o * o + b_o)
        preActivation = np.dot(input, outputWeight.T) + outputBias.T
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
    
    def initialiseWeights(self, inputSize, outputSize):
        """
        Initializes weights, biases, and hidden states for each hidden layer and the output layer.

        Args:
            inputSize (int): Size of the input feature vector.
            outputSize (int): Size of the output vector.
        """
        self.inputWeights = []
        self.hiddenWeights = []
        self.biases = []
        self.hiddenStates = []

        for i, hiddenSize in enumerate(self.hiddenSizes):
            inSize = inputSize 
            if(i != 0):
                inSize = self.hiddenSizes[i - 1]

            inputW = self._initialiseWeights(hiddenSize, inSize, self.hiddenStateActivationFunction)
            hiddenW = self._initialiseWeights(hiddenSize, hiddenSize, self.hiddenStateActivationFunction)
            bias = np.zeros((hiddenSize, 1))
            hiddenState = np.zeros((self.batchSize, hiddenSize))
        
            self.inputWeights.append(inputW)
            self.hiddenWeights.append(hiddenW)
            self.biases.append(bias)
            self.hiddenStates.append(hiddenState)

        self.outputWeight = self._initialiseWeights(outputSize, self.hiddenSizes[-1], self.outputLayerActivationFunction)
        self.outputBias = np.zeros((outputSize, 1))
    
        self.inputSize = inputSize
        self.outputSize = outputSize

    def backwardPropagation(self, inputs, outputs, targets):
        inputWeightGradients, hiddenStateWeightGradients, biasGradients, outputWeightGradients, outputbiasGradients = self._Stacked_BPTT(inputs, self.allHiddenStates, self.preActivations, self.outputPreAct, targets, outputs)
        Parameters =  {
            "I_W": self.inputWeights,
            "b": self.biases,
            "H_W": self.hiddenWeights,
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
        Trains the model on the given input data and labels using the Adam optimizer,
        then calculates and returns the loss.

        Args:
            inputData (ndarray): 3D array of input sequences with shape (batchSize, sequenceLength, inputSize).
            labels (ndarray): True labels corresponding to the input data.
            alpha (float, optional): Learning rate for the optimizer. Default is 0.001.
            beta1 (float, optional): Beta1 parameter for Adam optimizer. Default is 0.9.
            beta2 (float, optional): Beta2 parameter for Adam optimizer. Default is 0.999.
            epsilon (float, optional): Epsilon parameter for Adam optimizer to avoid division by zero. Default is 1e-8.

        Returns:
            float: Calculated loss between the model output and true labels.
        """
        assert np.array(inputData).ndim == 3, f"Dimension wrong size, got {np.array(inputData).ndim}, expected 3"
        AllOutputs = self.optimiser(inputData, labels, alpha, beta1, beta2, epsilon)
        AllOutputs = np.reshape(AllOutputs, (np.array(labels).shape))
        loss = self.lossFunction(AllOutputs, labels)
        return loss