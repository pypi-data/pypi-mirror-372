import numpy as np

class GlobalAveragePooling():
    def forward(self, inputTensor):
        """
        Performs global average pooling, reducing each feuture map to a single value.

        Args:
            inputTensor (ndarray): A 4D or 3D array representing the images with shape (batches, number of images, height, width).
        
        Returns:
            ndarray: A 3D array containing global averages for each feuture map for each batch.
        """
        self.inputShape = inputTensor.shape
        if(inputTensor.ndim == 4):
            output = np.mean(inputTensor, axis = (2, 3))
        elif(inputTensor.ndim == 3):
            output = np.mean(inputTensor, axis = (1, 2))
        else:
            raise ValueError(f"Input tensor incorrect dimension")
        return output

    def _backpropagation(self, gradient):   
        if(len(self.inputShape) == 4):
            batch_size, channels, height, width = self.inputShape
            grad = np.zeros((batch_size, channels, height, width), dtype=np.float64)
            for b in range(batch_size):
                for c in range(channels):
                    grad[b, c] = gradient[b, c] / (height * width)
        else:
            batch_size, channels, width = self.inputShape
            grad = np.zeros((batch_size, channels, width), dtype=np.float64)
            for b in range(batch_size):
                for c in range(channels):
                    grad[b, c] = gradient[b, c] / width
        return grad