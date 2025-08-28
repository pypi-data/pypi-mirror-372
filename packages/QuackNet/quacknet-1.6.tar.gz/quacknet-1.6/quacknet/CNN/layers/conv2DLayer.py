import numpy as np
import math

class Conv2DLayer():
    def __init__(self, kernalSize, depth, numKernals, stride, padding = "no"):
        """
        Initialises a convolutional layer.

        Args:
            kernalSize (int): The size of the covolution kernel (assumed it is a square).
            depth (int): Depth of the input tensor.
            numKernals (int): Number of kernels in this layer.
            stride (int): The stride length for convolution.
            padding (str or int, optional): Padding size or "no" for no padding. Default is "no".
        """
        self.kernalSize = kernalSize
        self.numKernals = numKernals
        self.kernalWeights = []
        self.kernalBiases = []
        self.depth = depth
        self.stride = stride
        self.padding = padding
        if(padding == "no" or padding == "n" or padding == "NO" or padding == "N"):
            self.usePadding = False
        else:
            self.padding = int(self.padding)
            self.usePadding = True
    
    def _padImage(self, inputTensor, kernalSize, strideLength, typeOfPadding): #pads image
        """
        Pads each image in the input tensor.

        Args:
            inputTensor (ndarray): A 3D array representing the images with shape (number of images, height, width).
            kernalSize (int): The size of the covolution kernel (assumed it is a square).
            strideLength (int): The stride length for convolution.
            typeOfPadding (int): The value used for padding the images.
        
        Returns:
            ndarray: A 3D array of padded images.
        """
        batch_size, depth, height, width = inputTensor.shape
        paddingSize = math.ceil(((strideLength - 1) * len(inputTensor) - strideLength + kernalSize) / 2)
        padded_height = height + 2 * paddingSize
        padded_width = width + 2 * paddingSize

        padded = np.full((batch_size, depth, padded_height, padded_width), typeOfPadding)

        for b in range(batch_size):
            for d in range(depth):
                padded[b, d, paddingSize:paddingSize + height, paddingSize:paddingSize + width] = inputTensor[b, d]

        return padded

    def forward(self, imageTensor):
        if(self.usePadding == True):
            imageTensor = self._padImage(imageTensor, self.kernalSize, self.stride, self.padding)

        outputHeight = (imageTensor.shape[2] - self.kernalSize) // self.stride + 1
        outputWidth = (imageTensor.shape[3] - self.kernalSize) // self.stride + 1
        
        assert outputHeight > 0 and outputWidth > 0

        batchSize, inputDepth, inputHeight, inputWidth = imageTensor.shape

        output = np.zeros((batchSize, self.numKernals, outputHeight, outputWidth))
        
        for b in range(batchSize):
            for k in range(self.numKernals):
                for i in range(outputHeight):
                    for j in range(outputWidth):
                        startI = i * self.stride
                        startJ = j * self.stride
                        region = imageTensor[b, :, startI: startI + self.kernalSize, startJ:startJ + self.kernalSize]
                        output[b, k, i, j] = np.sum(region * self.kernalWeights[k]) + self.kernalBiases[k]
        return output 
                    
    def _backpropagation(self, errorPatch, inputTensor):
        """
        Compute gradients for conolutional layer weights, biases and input errors during backpropagation.

        Args:
            errorPatch (ndarray): Error gradient from the next layer.
            inputTensor (ndarray): Input to the convolutional layer during forward propagation.
        
        Returns:
            weightGradients (ndarray): Gradients of the loss with respect to kernels.
            biasGradients (ndarray): Gradients of the loss with respect to biases for each kernel.
            inputErrorTerms (ndarray): Error terms propagated to the previous layer.
        """
        ###################################        
        # gets the error gradient from the layer infront and it is a error patch
        # this error patch is the same size as what the convolutional layer outputed during forward propgation
        # get the kernal (as in a patch of the image) again, but this time you are multipling each value in the kernal by 1 value that is inside the error patch
        # this makes the gradient of the loss of one kernal's weight
        
        # the gradient of the loss of one kernal's bias is the summ of all the error terms
        # because bias is applied to every input in forward propgation
        
        # the gradient of the loss of the input, which is the error terms for the layer behind it
        # firstly the kernal has to be flipped, meaning flip the kernal left to right and then top to bottom, but not flipping the layers,
        # the gradient of one pixel, is the summ of each error term multiplied by the flipped kernal 
        ###################################     
        
        batch_size, in_depth, in_h, in_w = inputTensor.shape
        _, num_kernels, out_h, out_w = errorPatch.shape
        k = self.kernalSize
        s = self.stride

        weightGradients = np.zeros((self.numKernals, self.depth, k, k))
        biasGradients = np.zeros((self.numKernals,))
        inputErrorTerms = np.zeros_like(inputTensor)

        flippedKernels = self.kernalWeights[:, :, ::-1, ::-1]

        for b in range(batch_size):
            for k_i in range(self.numKernals):
                for i in range(out_h):
                    for j in range(out_w):
                        start_i = i * s
                        start_j = j * s
                        region = inputTensor[b, :, start_i:start_i + k, start_j:start_j + k]
                        weightGradients[k_i] += errorPatch[b, k_i, i, j] * region
                        inputErrorTerms[b, :, start_i:start_i + k, start_j:start_j + k] += errorPatch[b, k_i, i, j] * flippedKernels[k_i]

        biasGradients = np.sum(errorPatch, axis=(0, 2, 3))
        return weightGradients, biasGradients, inputErrorTerms
        
        