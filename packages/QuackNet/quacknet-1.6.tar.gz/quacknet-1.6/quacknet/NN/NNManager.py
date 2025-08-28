from quacknet.NN import backPropgation
from quacknet.core.activations.activationFunctions import relu, sigmoid, tanH, linear, softMax
from quacknet.core.losses.lossFunctions import MSELossFunction, MAELossFunction, CrossEntropyLossFunction
from quacknet.NN.initialisers import Initialisers
from quacknet.NN.writeAndReadWeightBias import writeAndRead
from quacknet.core.utilities.dataAugmentation import Augementation
from quacknet.core.optimisers.adam import Adam
import numpy as np

class Network(Initialisers, writeAndRead, Augementation):
    def __init__(self, lossFunc = "MSE", learningRate = 0.01, useBatches = False, batchSize = 32, optimisationFunction = Adam):
        """
        Args:
            lossFunc (str): Loss function name ('mse', 'mae', 'cross'). Default is "MSE".
            learningRate (float, optional): Learning rate for training. Default is 0.01.
            optimisationFunc (str, optional): Optimisaztion method ('gd', 'sgd', 'batching'). Default is "gd".
            useBatches (bool, optional): Wether to use mini batches. Default is False.
            batchSize (int, optional): size of mini batches. Default is 32.
        """
        self.layers = []
        self.weights = []
        self.biases = []
        self.learningRate = learningRate

        lossFunctionDict = {
            "mse": MSELossFunction,
            "mae": MAELossFunction,
            "cross entropy": CrossEntropyLossFunction,"cross": CrossEntropyLossFunction,
        }
        self.lossFunction = lossFunctionDict[lossFunc.lower()]

        self.optimisationFunction = optimisationFunction(self.forwardPropagation, self._backPropgation)

        self.useBatches = useBatches
        self.batchSize = batchSize

    def addLayer(self, size, activationFunction="relu"):
        """
        Add a layer to the network with the specified number of nodes and activation function.

        Args:
            size (int): Number of nodes in the new layer.
            activationFunction (str, optional): Activation function name ('relu', 'sigmoid', 'linear', 'tanh', 'softmax'). Default is "relu".
        """
        funcs = {
            "relu": relu,
            "sigmoid": sigmoid,
            "linear": linear,
            "tanh": tanH,
            "softmax": softMax,
        }
        if(activationFunction.lower() not in funcs):
            raise ValueError(f"Activation function not made: {activationFunction.lower()}")
        self.layers.append([size, funcs[activationFunction.lower()]])

    def _calculateLayerNodes(self, lastLayerNodes, lastLayerWeights, biases, currentLayer) -> np.ndarray:
        """
        Calculate the output of a layer given inputs, weights and biases.

        Args:
            lastLayerNodes (ndarray): Output from the previous layer.
            lastLayerWeights (ndarray): Weights connecting the previous layer.
            biases (ndarray): Biases of the current layer.
            currentLayer (list): List containing layer size and activation function.
        
        Returns:
            ndarray: Output of the current layer.
        """
        summ = np.dot(lastLayerNodes, lastLayerWeights) + biases
        if(currentLayer[1] != softMax):
            return currentLayer[1](summ)
        else:
            return softMax(summ)
        
    def forwardPropagation(self, inputData):
        """
        Perform forward propagation through the network for the given input data.

        Args:
            inputData (list): Input data for the network.

        Returns:
            list of ndarray: List containing outputs of each layer including input layer.
        """
        layerNodes = [np.array(inputData)]
        for i in range(1, len(self.layers)):
            layerNodes.append(np.array(self._calculateLayerNodes(layerNodes[i - 1], self.weights[i - 1], self.biases[i - 1], self.layers[i])))
        return layerNodes
    
    def _backPropgation(self, layerNodes, trueValues, returnErrorTermForCNN = False):
        """
        Perform backpropagation over the network layers to compute gradients for weights and biases.

        Args:
            layerNodes (list of ndarray): List of output values for each layer.
            weights (list of ndarray): List of weights for each layer.
            biases (list of ndarray): List of biases for each layer.
            trueValues (ndarray): True target values for the output layer.
            returnErrorTermForCNN (bool, optional): Whether to return error terms for CNN backpropagation. Defaults to False.

        Returns:
            weightGradients (list of ndarray): Gradients of weights for each layer.
            biasGradients (list of ndarray): Gradients of biases for each layer.
            If returnErrorTermForCNN is True:
                hiddenWeightErrorTermsForCNNBackpropgation (ndarray): Error terms from the output layer weights.   
        """  
        if(returnErrorTermForCNN):
            return backPropgation._backPropgation(layerNodes, self.weights, self.biases, trueValues, self.layers, self.lossFunction, returnErrorTermForCNN)
        else:
            weightGradients, biasGradients = backPropgation._backPropgation(layerNodes, self.weights, self.biases, trueValues, self.layers, self.lossFunction, returnErrorTermForCNN)
        
        Parameters =  {
            "weight": self.weights,
            "biases": self.biases,
        }
  
        Gradients =  {
            "weight": weightGradients,
            "biases": biasGradients,
        }
        return Parameters, Gradients 

    def optimise(self, inputData, labels, learningRate, batchSize):
        return self.optimisationFunction.optimiser(inputData, labels, self.useBatches, batchSize, learningRate) 

    def train(self, inputData, labels, epochs):
        """
        Train the neural network using the specified optimisation function.

        Args:
            inputData (list of lists): All of the training input data
            labels (list of ndarray): All of the labels for all the input data.
            epochs (int): Number of training epochs.
        
        Returns:
            float: Average accauracy over all epochs.
            float: Average loss over all epochs.
        """
        assert np.array(inputData).ndim == 2, f"Dimension wrong size, got {np.array(inputData).ndim}, expected 2"
        self._checkIfNetworkCorrect()
        correct = 0
        totalLoss = 0
        nodes, Parameters = self.optimise(inputData, labels, self.learningRate, self.batchSize)        
        self.weights = Parameters["weight"]
        self.biases = Parameters["biases"]
        
        lastLayer = len(nodes[0]) - 1
        if(epochs > 1):
            labels = np.tile(labels, (epochs, 1)) # duplicates the labels ([1, 2], (3, 1)) would become [[1, 2], [1, 2], [1, 2]]
        for i in range(len(nodes)): 
            totalLoss += self.lossFunction(nodes[i][lastLayer], labels[i])
            nodeIndex = np.argmax(nodes[i][lastLayer])
            labelIndex = np.argmax(labels[i])
            if(nodeIndex == labelIndex):
                correct += 1
        return correct / (len(labels) * epochs), totalLoss / (len(labels) * epochs)
    
    def _checkIfNetworkCorrect(self): #this is to check if activation functions/loss functions adhere to certain rule
        for i in range(len(self.layers) - 1): #checks if softmax is used for any activation func that isnt output layer
            if(self.layers[i][1] == softMax): #if so it stops the user
                raise ValueError(f"Softmax shouldnt be used in non ouput layers. Error at Layer {i + 1}")
        usingSoftMax = self.layers[len(self.layers) - 1][1] == softMax
        if(usingSoftMax == True):
            if(self.lossFunction != CrossEntropyLossFunction): #checks if softmax is used without cross entropy loss function
                raise ValueError(f"Softmax output layer requires Cross Entropy loss function") #if so stops the user
        elif(self.lossFunction == CrossEntropyLossFunction):
            raise ValueError(f"Cross Entropy loss function requires Softmax output layer") #if so stops the user
    