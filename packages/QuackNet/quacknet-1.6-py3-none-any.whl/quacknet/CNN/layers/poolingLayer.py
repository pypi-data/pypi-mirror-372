import numpy as np

class PoolingLayer():
    def __init__(self, gridSize, stride, mode = "max"):
        """
        Initialises a pooling layer.

        Args:
            gridSize (int): The size of the pooling window.
            stride (int): The stride length for pooling.
            mode (str, optional): Pooling mode of "max", "ave" (average). Default is "max".        
        """
        self.gridSize = gridSize
        self.stride = stride
        self.mode = mode.lower()
    
    def forward(self, inputTensor):
        """
        Applies pooling (max or average) to reduce the size of the batch of inputs.

        Args:
            inputTensor (ndarray): A 4D or 3D array representing the images with shape (number of images, height, width).

        Returns:
            ndarray: A 3D array of feuture maps with reduced shape.
        """
        if(self.mode.lower() == "max"):
            poolFunc = np.max
        elif(self.mode.lower() == "ave"):
            poolFunc = np.mean
        else:
            raise ValueError(f"pooling mode isnt correct: '{self.mode}', expected 'max' or 'ave'")

        if(inputTensor.ndim == 4):
            batch_size, channels, height, width = inputTensor.shape
            outputHeight = (height - self.gridSize) // self.stride + 1
            outputWidth = (width - self.gridSize) // self.stride + 1

            output = np.zeros((batch_size, channels, outputHeight, outputWidth))
            
            for b in range(batch_size):
                for c in range(channels):
                    for x in range(outputHeight):
                        for y in range(outputWidth):
                            startX = x * self.stride
                            startY = y * self.stride
                            window = inputTensor[b, c, startX:startX+self.gridSize, startY:startY+self.gridSize]
                            output[b, c, x, y] = poolFunc(window)
        
        elif(inputTensor.ndim == 3):
            batch_size, height, width = inputTensor.shape
            outputHeight = (height - self.gridSize) // self.stride + 1
            outputWidth = (width - self.gridSize) // self.stride + 1

            output = np.zeros((batch_size, outputHeight, outputWidth))
            
            for b in range(batch_size):
                for x in range(outputHeight):
                    for y in range(outputWidth):
                        startX = x * self.stride
                        startY = y * self.stride
                        window = inputTensor[b, startX:startX+self.gridSize, startY:startY+self.gridSize]
                        output[b, x, y] = poolFunc(window)
        else:
            raise ValueError("Input tensor wrong dimension")

        return output

    def _backpropagation(self, errorPatch, inputTensor):
        """
        Performs backpropagation through the pooling layer.

        Args:
            errorPatch (ndarray): Error gradient from the next layer.
            inputTensor (ndarray): Input tensor during forward propagation.
        
        Returns:
            inputGradient (ndarray): Gradient of the loss.
        """
        if(self.mode == "max"):
            return self._MaxPoolingDerivative(errorPatch, inputTensor, self.gridSize, self.stride)
        elif(self.mode == "ave"):
            return self._AveragePoolingDerivative(errorPatch, inputTensor, self.gridSize, self.stride)

    def _MaxPoolingDerivative(self, errorPatch, inputTensor, sizeOfGrid, strideLength):
        """
        Compute the gradient of the loss with respect to the input of the max pooling layer during backpropagation.

        Args:
            errorPatch (ndarray): Error gradient from the next layer.
            inputTensor (ndarray): Input to the max pooling layer during forward propagation.
            sizeOfGrid (int): Size of the pooling window.
            strideLength (int): Stride length used during pooling.
        
        Returns:
            inputGradient (ndarray): Gradient of the loss with respect to the inputTensor
        """
        if(inputTensor.ndim == 4):
            batch_size, channels, height, width = inputTensor.shape
            sizeOfGrid = self.gridSize
            strideLength = self.stride
            
            inputGradient = np.zeros_like(inputTensor, dtype=np.float64)
            outputHeight = (height - sizeOfGrid) // strideLength + 1
            outputWidth = (width - sizeOfGrid) // strideLength + 1
            
            for b in range(batch_size):
                for c in range(channels):
                    for x in range(outputHeight):
                        for y in range(outputWidth):
                            startX = x * strideLength
                            startY = y * strideLength
                            window = inputTensor[b, c, startX:startX+sizeOfGrid, startY:startY+sizeOfGrid]
                            maxIndex = np.argmax(window)
                            maxX, maxY = divmod(maxIndex, sizeOfGrid)
                            inputGradient[b, c, startX+maxX, startY+maxY] += errorPatch[b, c, x, y]
        
        elif(inputTensor.ndim == 3):
            batch_size, height, width = inputTensor.shape
            sizeOfGrid = self.gridSize
            strideLength = self.stride
            
            inputGradient = np.zeros_like(inputTensor, dtype=np.float64)
            outputHeight = (height - sizeOfGrid) // strideLength + 1
            outputWidth = (width - sizeOfGrid) // strideLength + 1
            
            for b in range(batch_size):
                for x in range(outputHeight):
                    for y in range(outputWidth):
                        startX = x * strideLength
                        startY = y * strideLength
                        window = inputTensor[b, startX:startX+sizeOfGrid, startY:startY+sizeOfGrid]
                        maxIndex = np.argmax(window)
                        maxX, maxY = divmod(maxIndex, sizeOfGrid)
                        inputGradient[b, startX+maxX, startY+maxY] += errorPatch[b, x, y]
        else: 
            raise ValueError("Input tensor wrong dimension")

        return inputGradient

    def _AveragePoolingDerivative(self, errorPatch, inputTensor, sizeOfGrid, strideLength):
        """
        Compute the gradient of the loss with respect to the input of the average pooling layer during backpropagation.

        Args:
            errorPatch (ndarray): Error gradient from the next layer.
            inputTensor (ndarray): Input to the average pooling layer during forward propagation.
            sizeOfGrid (int): Size of the pooling window.
            strideLength (int): Stride length used during pooling.
        
        Returns:
            inputGradient (ndarray): Gradient of the loss with respect to the inputTensor
        """       
        if(inputTensor.ndim == 4):
            batch_size, channels, height, width = inputTensor.shape
            sizeOfGrid = self.gridSize
            strideLength = self.stride
            
            inputGradient = np.zeros_like(inputTensor, dtype=np.float32)
            outputHeight = (height - sizeOfGrid) // strideLength + 1
            outputWidth = (width - sizeOfGrid) // strideLength + 1
            avgMultiplier = 1 / (sizeOfGrid ** 2)
            
            for b in range(batch_size):
                for c in range(channels):
                    for x in range(outputHeight):
                        for y in range(outputWidth):
                            startX = x * strideLength
                            startY = y * strideLength
                            inputGradient[b, c, startX:startX+sizeOfGrid, startY:startY+sizeOfGrid] += errorPatch[b, c, x, y] * avgMultiplier
        
        elif(inputTensor.ndim == 3):
            batch_size, height, width = inputTensor.shape
            sizeOfGrid = self.gridSize
            strideLength = self.stride
            
            inputGradient = np.zeros_like(inputTensor, dtype=np.float32)
            outputHeight = (height - sizeOfGrid) // strideLength + 1
            outputWidth = (width - sizeOfGrid) // strideLength + 1
            avgMultiplier = 1 / (sizeOfGrid ** 2)
            
            for b in range(batch_size):
                for x in range(outputHeight):
                    for y in range(outputWidth):
                        startX = x * strideLength
                        startY = y * strideLength
                        inputGradient[b, startX:startX+sizeOfGrid, startY:startY+sizeOfGrid] += errorPatch[b, x, y] * avgMultiplier
        else: 
            raise ValueError("Input tensor wrong dimension")
        
        return inputGradient