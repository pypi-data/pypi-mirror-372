from .CNN import CNNModel
from .CNN import Conv1DLayer, Conv2DLayer, ActivationLayer, DenseLayer, PoolingLayer, GlobalAveragePooling

from .Transformer import EmbeddingLayer, FeedForwardNetwork, MultiAttentionHeadLayer, NormLayer, PositionalEncoding, ResidualConnection
from .Transformer import TransformerBlock, Transformer

from .RNN import StackedRNN, SingularRNN

from .core.losses.lossFunctions import *
from .core.losses.lossDerivativeFunctions import *

from .core.activations.activationFunctions import *
from .core.activations.activationDerivativeFunctions import *

from .core.utilities.dataAugmentation import *
from .core.utilities.drawGraphs import *

from .core.optimisers.adam import Adam
from .core.optimisers.stochasticGD import SGD
from .core.optimisers.gradientDescent import GD

from .NN import Network

"""
# QuackNet

**QuackNet** is a Python based building and training neural networks and convolutional networks entirely from scratch. It offers foundational implementations of key components such as forward propagation, backpropagation and optimisation algorithms, without relying on machine learning frameworks like TensorFlow or PyTorch

## Key Features

**1. Custom Implementation:**
-   Fully handwritten layers, activation functions and loss functions.
-   No reliance on external libraries for machine learning (except for numpy)

**2. Core neural network functionality:**
-   Support for common activation functions (eg.Leaky ReLU, Sigmoid, Softmax)
-   Multiple loss functions with derivatives (eg. MSE, MAE, Cross entropy)

**3. Training:**
-   includes backpropagation for gradient calculation and parameter updates
-   Optimisers: Gradient Descent, Stochastic Gradient Descent (SGD), and Adam optimiser.
-   Supports batching for efficient training.

**4. Layer Support:**
-   Fully Connected Layer (Dense)
-   Convolutional
-   Pooling (Max and Average)
-   Global Average Pooling
-   Activation Layers

**5. Additional Features:**
-   Save and load model weights and biases.
-   Evaluation metrics including accuracy and loss.
-   Visualisation tools for training progress.
-   Demo projects like MNIST and HAM10000 classification.

## Installation

QuackNet is simple to install via PyPI.

**Install via PyPI**

```
pip install QuackNet
```

## Usage Example

```Python
from quacknet.main import Network

# Define a neural network architecture
n = Network(
    lossFunc = "cross entropy",
    learningRate = 0.01,
    optimisationFunc = "sgd", #stochastic gradient descent
)
n.addLayer(3, "relu") # Input layer
n.addLayer(2, "relu") # Hidden layer
n.addLayer(1, "softmax") # Output layer
n.createWeightsAndBiases()

# Example data
inputData = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
labels = [[1], [0]]

# Train the network
accuracy, averageLoss = n.train(inputData, labels, epochs = 10)

# Evaluate
print(f"Accuracy: {accuracy}%")
print(f"Average loss: {averageLoss}")
```

## Examples

-   [Simple Neural Network Example](/ExampleCode/NNExample.py): A basic neural network implementation demonstrating forward and backpropagation
-   [Convolutional Neural Network Example](/ExampleCode/CNNExample.py): Shows how to use the convolutional layers in the library
-   [MNIST Neural Network Example](/ExampleCode/MNISTExample/mnistExample.py): Shows how to use neural network to train on MNIST

## Highlights

-   **Custom Architectures:** Define and train neural networks with fully customisable architectures
-   **Optimisation Algorithms:** Includes Gradient Descent, Stochastic Gradient Descent and Adam optimiser for efficient training
-   **Loss and Activation Functions:** Prebuilt support for common loss and activation functions with the option to make your own
-   **Layer Support:**
    -   Fully Connected (Dense)
    -   Convolutional
    -   Pooling (max and Average)
    -   Global Average Pooling
    -   Activation layer
-   **Evaluation Tools:** Includes metrics for model evaluation such as accuracy and loss
-   **Save and Load:** Save weights and biases for reuse for further training
-   **Demo Projects:** Includes example implementations such as MNIST digit classification

## Code structure

### Neural Network Class
-   **Purpose** Handles fully connected layers for standard neural network
-   **Key Components:**
    -   Layers: Dense Layer
    -   Functions: Forward propagation, backpropagation
    -   Optimisers: SGD, GD, GD using batching

### Convolutional Neural Network Class
-   **Purpose** Specialised for image data processing using convolutional layers
-   **Key Components:**
    -   Layers: Convolutional, pooling, dense and activation layers
    -   Functions: Forward propagation, backpropagation, flattening, global average pooling
    -   Optimisers: Adam optimiser, SGD, GD, GD using batching

## Related Projects

### Skin Lesion Detector

A convolutional neural network (CNN) skin lesion classification model built with QuackNet, trained using the HAM10000 dataset. This model achieved 60.2% accuracy on a balanced validation set.

You can explore the full project here:
[Skin Lesion Detector Repository](https://github.com/SirQuackPng/skinLesionDetector)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
"""
