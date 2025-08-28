import numpy as np

class writeAndRead: 
    def write(self, pathToWeight="ExampleCode/MNISTExample/WeightsAndBiases/weights.txt", pathToBias="ExampleCode/MNISTExample/WeightsAndBiases/biases.txt"):
        weightFile = open(pathToWeight, "w")
        for a in range(len(self.weights)):
            for b in range(len(self.weights[a])):
                currLine = " ".join(map(str, self.weights[a][b]))
                weightFile.write(currLine + "\n")
            weightFile.write("\n")
        weightFile.close()

        biasFile = open(pathToBias, "w")
        for a in range(len(self.biases)):
            currLine = " ".join(map(str, self.biases[a]))
            biasFile.write(currLine + "\n")
        biasFile.close()
    
    def read(self, pathToWeight="ExampleCode/MNISTExample/WeightsAndBiases/weights.txt", pathToBias="ExampleCode/MNISTExample/WeightsAndBiases/biases.txt"):
        weightFile = open(pathToWeight, "r")
        layerWeights = []
        for line in weightFile:
            line = line.strip()
            if(line == ""):
                if(len(layerWeights) > 0):
                    self.weights.append(np.array(layerWeights))
                layerWeights = []
            else:
                l = []
                for i in line.split():
                    l.append(float(i))
                layerWeights.append(l)
        
        if(len(layerWeights) > 0):
            self.weights.append(layerWeights)
        weightFile.close()

        biasFile = open(pathToBias, "r")
        layerWeights = []
        for line in biasFile:
            line = line.strip()
            if(line != ""):
                line = list(map(float, line.split()))
                self.biases.append(line)
        biasFile.close()