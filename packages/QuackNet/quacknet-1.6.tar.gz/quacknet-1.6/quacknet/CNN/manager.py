from quacknet.CNN.layers.activationLayer import ActivationLayer
from quacknet.CNN.layers.conv2DLayer import Conv2DLayer
from quacknet.CNN.layers.conv1DLayer import Conv1DLayer
from quacknet.CNN.layers.poolingLayer import PoolingLayer
from quacknet.CNN.layers.globalAveragePoolingLayer import GlobalAveragePooling
from quacknet.CNN.layers.denseLayer import DenseLayer
from quacknet.core.optimisers.adam import Adam
import numpy as np

class CNNModel:
    def __init__(self, NeuralNetworkClass):
        self.layers = []
        self.weights = []
        self.biases = []
        self.NeuralNetworkClass = NeuralNetworkClass
        self.adam = Adam(self.forward, self._backpropagation)
    
    def addLayer(self, layer):
        """
        Adds a layer to the CNN model.

        Args:
            layer (class): ConvLayer, PoolingLayer, GlobalAveragePoolingLayer, ActivationLayer, and DenseLayer
        """
        self.layers.append(layer)
    
    def forward(self, inputTensor):
        """
        Performs a forward pass through all layers.

        Args:
            inputTensor (ndarray): Input data tensor to the CNN.
        
        Returns:
            list: List of tensors output by each layer including the input.
        """
        allTensors = [inputTensor]
        for layer in self.layers:
            inputTensor = layer.forward(inputTensor)
            allTensors.append(inputTensor)
        return allTensors

    def _backpropagation(self, allTensors, trueValues):
        """
        Performs backpropagation through all layers to compute gradients.

        Args:
            allTensors (list): List of all layer outputs from forward propagation.
        
        Returns:
            allWeightGradients (list): List of all the weight gradients calculated during backpropgation.
            allBiasGradients (list): List of all the bias gradients calculated during backpropgation.
        """
        weightGradients, biasGradients, errorTerms = self.layers[-1]._backpropagation(trueValues) # <-- this is a neural network 
        allWeightGradients = [weightGradients]
        allBiasGradients = [biasGradients]
        for i in range(len(self.layers) - 2, -1, -1):
            if(type(self.layers[i]) == GlobalAveragePooling):
                errorTerms = self.layers[i]._backpropagation(errorTerms)
            if(type(self.layers[i]) == PoolingLayer or type(self.layers[i]) == ActivationLayer):
                errorTerms = self.layers[i]._backpropagation(errorTerms, allTensors[i])
            elif(type(self.layers[i]) == Conv2DLayer or type(self.layers[i]) == Conv1DLayer):
                weightGradients, biasGradients, errorTerms = self.layers[i]._backpropagation(errorTerms, allTensors[i])
                allWeightGradients.insert(0, weightGradients)
                allBiasGradients.insert(0, biasGradients)
        
        Parameters =  {
            "weight": self.weights,
            "biases": self.biases,
        }
  
        Gradients =  {
            "weight": allWeightGradients,
            "biases": allBiasGradients,
        }
        return Parameters, Gradients 
    
    def _optimser(self, inputData, labels, useBatches, batchSize, alpha, beta1, beta2, epsilon):
        """
        Runs the Adam optimiser either with or without batches.

        Args:
            inputData (ndarray): All the training data.
            labels (ndarray): All the true labels for the training data.
            useBatches (bool): Whether to use batching.
            weights (list): Current weights.
            biases (list): Current biases.
            batchSize (int): Size of batches.
            alpha (float): Learning rate.
            beta1 (float): Adam's beta1 parameter.
            beta2 (float): Adam's beta2 parameter.
            epsilon (float): Adam's epsilon parameter.
        
        Returns:
            list: The nodes (returned to calculate accuracy and loss).
            list: Updated weights after optimisation
            list: Updated biases after optimisation
        """
        allOutputs, Parameters = self.adam.optimiser(inputData, labels, useBatches, batchSize, alpha, beta1, beta2, epsilon)
        self.weights = Parameters["weight"]
        self.biases = Parameters["biases"]
        return allOutputs, Parameters
    
    def train(self, inputData, labels, useBatches, batchSize, alpha = 0.001, beta1 = 0.9, beta2 = 0.999, epsilon = 1e-8):
        """
        Trains the CNN for one epoch and calculates accuracy and average loss.

        Args:
            inputData (ndarray): All the training data.
            labels (ndarray): All the true labels for the training data.
            useBatches (bool): Whether to use batching.
            batchSize (int): Size of batches.
            alpha (float, optional): Learning rate. Default is 0.001.
            beta1 (float, optional): Adam's beta1 parameter. Default is 0.9.
            beta2 (float, optional): Adam's beta2 parameter. Default is 0.999.
            epsilon (float, optional): Adam's epsilon parameter. Default is 1e-8.

        Returns:
            float: accuracy percentage.
            float: average loss.
        """
        # InputData: (numImages, channels, height, width)   or (numImages, channels, width)  <--- if using Conv1D layer
        assert np.array(inputData).ndim == 4 or np.array(inputData).ndim == 3, f"Dimension wrong size, got {np.array(inputData).ndim}, expected 4 or 3"
        correct, totalLoss = 0, 0
        
        nodes, _ = self._optimser(inputData, labels, useBatches, batchSize, alpha, beta1, beta2, epsilon)        
        
        #nodes: (numbatches, numLayers, batchSize, outputSize)

        #lastLayer = len(nodes[0]) - 1
        #for i in range(len(nodes)): 
        #    totalLoss += self.NeuralNetworkClass.lossFunction(nodes[i][lastLayer], labels[i])
        #    nodeIndex = np.argmax(nodes[i][lastLayer])
        #    labelIndex = np.argmax(labels[i])
        #    
        #    if(nodeIndex == labelIndex):
        #        correct += 1

        if(useBatches == False): 
            batchSize = 1

        for batch in range(len(nodes)): 
            lastLayer = nodes[batch][-1] # shape: (batchSize, outputSize) <-- last layer so is the FNN
            for miniBatch in range(len(lastLayer)): #shape: (outputSize)
                totalLoss += self.NeuralNetworkClass.lossFunction(lastLayer[miniBatch], labels[batch * batchSize + miniBatch])
                nodeIndex = np.argmax(lastLayer[miniBatch])
                labelIndex = np.argmax(labels[batch * batchSize + miniBatch])
                
                if(nodeIndex == labelIndex):
                    correct += 1


        return 100 * (correct / len(labels)), totalLoss / len(labels)
    
    def createWeightsBiases(self):
        """
        Initialises weights and biases for convolutional and dense layers.
        """
        for i in range(len(self.layers)):
            if(type(self.layers[i]) == Conv2DLayer):
                kernalSize = self.layers[i].kernalSize
                numKernals = self.layers[i].numKernals
                depth = self.layers[i].depth

                bounds =  np.sqrt(2 / kernalSize) # He initialisation

                self.weights.append(np.random.normal(0, bounds, size=(numKernals, depth, kernalSize, kernalSize)))
                self.biases.append(np.zeros((numKernals)))

                self.layers[i].kernalWeights = self.weights[-1]
                self.layers[i].kernalBiases = self.biases[-1]
            elif(type(self.layers[i]) == Conv1DLayer):
                kernalSize = self.layers[i].kernalSize
                numKernals = self.layers[i].numKernals

                bounds =  np.sqrt(2 / kernalSize) # He initialisation

                self.weights.append(np.random.normal(0, bounds, size=(numKernals, kernalSize, kernalSize)))
                self.biases.append(np.zeros((numKernals)))

                self.layers[i].kernalWeights = self.weights[-1]
                self.layers[i].kernalBiases = self.biases[-1]

            elif(type(self.layers[i]) == DenseLayer):
                self.weights.append(self.layers[i].NeuralNetworkClass.weights)
                self.biases.append(self.layers[i].NeuralNetworkClass.biases)

    def saveModel(self, NNweights, NNbiases, CNNweights, CNNbiases, filename = "modelWeights.npz"):
        """
        Saves model weights and biases to a compressed npz file.

        Args:
            NNweights (list): Weights of the dense neural network layers.
            NNbiases (list): Biases of the dense neural network layers.
            CNNweights (list): Weights of the convolutional layers.
            CNNbiases (list): Biases of the convolutional layers.
            filename (str, optional): Filename to save the weights. Default is "modelWeights.npz".
        """
        CNNweights = np.array(CNNweights, dtype=object)
        CNNbiases = np.array(CNNbiases, dtype=object)
        NNweights = np.array(NNweights, dtype=object)
        NNbiases = np.array(NNbiases, dtype=object)
        np.savez_compressed(filename, CNNweights = CNNweights, CNNbiases = CNNbiases, NNweights = NNweights, NNbiases = NNbiases, allow_pickle = True)

    def loadModel(self, neuralNetwork, filename = "modelWeights.npz"):
        """
        Loads model weights and biases from a compressed npz file and assigns them to layers.
        
        Args:
            neuralNetwork (class): The dense neural network to load weights into.
            filename (str, optional): Filename to save the weights. Default is "modelWeights.npz".
        """
        data = np.load(filename, allow_pickle = True)
        CNNweights = data["CNNweights"]
        CNNbiases = data["CNNbiases"]
        NNweights = data["NNweights"]
        NNbiases = data["NNbiases"]

        self.layers[-1].NeuralNetworkClass.weights = NNweights
        self.layers[-1].NeuralNetworkClass.biases = NNbiases
        neuralNetwork.weights = NNweights
        neuralNetwork.biases = NNbiases
        self.weights = CNNweights
        self.biases = CNNbiases

        currWeightIndex = 0
        for i in range(len(self.layers)):
            if(type(self.layers[i]) == Conv2DLayer or type(self.layers[i]) == Conv1DLayer):
                self.layers[i].kernalWeights = CNNweights[currWeightIndex]
                self.layers[i].kernalBiases = CNNbiases[currWeightIndex]
                currWeightIndex += 1
