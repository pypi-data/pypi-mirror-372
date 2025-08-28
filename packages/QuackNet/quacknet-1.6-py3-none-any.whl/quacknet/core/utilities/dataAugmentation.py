import numpy as np
from PIL import Image
import os

class Augementation:
    def hotEncodeLabels(self, allLabels, numClasses):
        """
        Converts a list of integer labels into one hot encoded format

        Args:
            allLabels (list of lists): All of the labels of the input data.
            numClasses (int): The total number of classes.
        
        Returns:
            list of ndarray: a 2D array of hot encoded labels.
        """
        labels = np.zeros((len(allLabels), numClasses))
        for i in range(len(allLabels)):
            labels[i][allLabels[i]] = 1
        return labels

    def getImagePaths(self, folderPath, extensions = ['.jpg', '.png', '.jpeg']):
        """
        Retrieves paths of all image files in a directory and its subdirectories.

        Args:
            folderPath (str): The path to the directory containing images.
            extensions (list of str, optional): A list of file extensions to get as images. Default is ['.jpg', '.png', '.jpeg'].

        Returns:
            list of str: A list of full paths to image files.
        """
        imagePaths = []
        for root, dirs, files in os.walk(folderPath):
            for file in files:
                if(any(file.lower().endswith(ext) for ext in extensions)):
                    fullPath = os.path.join(root, file)
                    imagePaths.append(fullPath)
        return imagePaths

    def preprocessImages(self, imagePaths, targetSize = (128, 128)):
        """
        Loads and preprocesses images by resising and normalising them.

        Args:
            imagePaths (list of str): A list of full paths to image files.
            targetSize (tuple of int, optional): The desired size of the output images (width, height). Default is (128, 128).
        
        Returns:
            ndarray: A list of preprocessed images with values normalised between 0 to 1.
        """
        images = []
        for path in imagePaths:
            img = Image.open(path).convert('RGB')
            resized = img.resize(targetSize)
            normalised = np.array(resized) / 255.0
            images.append(normalised)
        return np.array(images)

    def dataAugmentation(self, images, labels):
        """
        Performs basic data augmentation by flipping horizontally and vertically.

        Args:
            images (ndarray): A list of images to augment
        
        Returns:
            ndarray: A list containing the augmented and original images.
            ndarray: A list containing the labels for the augmented images.
        """
        allImages = []
        allLabels = []
        for img in images:
            allImages.append(img)
            allImages.append(np.fliplr(img))
            allImages.append(np.flipud(img))
            allImages.append(np.flipud(np.fliplr(img)))

            allLabels.append(labels)
            allLabels.append(labels)
            allLabels.append(labels)
            allLabels.append(labels)
        return np.array(allImages), np.array(allLabels)