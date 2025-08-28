import numpy as np
import matplotlib.pyplot as plt

def drawGraphs(allAccuracy, allLoss):
    """
    Plot training accuracy and loss graphs over epochs for multiple runs.

    Args:
        allAccuracy (list of lists): Accuracy at each epoch for each run.
        allLoss (list of lists): Loss at each epoch for each run.

    Displays:
        Matplotlib plots of accuracy and loss trends.
    """

    if(len(allAccuracy) == 0 or len(allLoss) == 0):
        raise ValueError(f"allAcuracy or allLoss is empty")
    
    epochs = list(range(1, len(allAccuracy[0]) + 1))
    figure, axis = plt.subplots(1, 2)
    meanAccuracy = np.mean(allAccuracy, axis=0)
    meanLoss = np.mean(allLoss, axis=0)

    for i in range(len(allAccuracy)):
        axis[0].plot(epochs, allAccuracy[i], marker="o", label=f'Run {i+1}', alpha=0.3)
    axis[0].plot(epochs, meanAccuracy, marker="o", label=f'Average', alpha=1)
    axis[0].set_xticks(epochs)
    axis[0].set_xlabel("epochs")
    axis[0].set_ylabel("accauracy")
    axis[0].set_title("model accuracy")
    axis[0].grid(True)
    axis[0].legend()

    for i in range(len(allLoss)):
        axis[1].plot(epochs, allLoss[i], marker="o", label=f'Run {i+1}', alpha=0.3)
    axis[1].plot(epochs, meanLoss, marker="o", label=f'Average', alpha=1)
    axis[1].set_xticks(epochs)
    axis[1].set_xlabel("epochs")
    axis[1].set_ylabel("loss")
    axis[1].set_title("model loss")
    axis[1].grid(True)
    axis[1].legend()

    plt.tight_layout()
    plt.show()