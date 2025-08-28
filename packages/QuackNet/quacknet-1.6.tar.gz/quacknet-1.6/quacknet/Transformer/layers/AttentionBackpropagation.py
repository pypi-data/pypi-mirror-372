import numpy as np

class MultiHeadAttentionBackpropagation:
    def __init__(self, embededDimension, outputWeights, QueryWeights, KeyWeights, ValueWeights):
        self.embededDimension = embededDimension
        self.outputWeights = outputWeights
        self.QueryWeights = QueryWeights
        self.KeyWeights = KeyWeights
        self.ValueWeights = ValueWeights

    def backPropagation(self, originalInput, batchSize, sequenceLength, outputGradient, attentionHeads, attentionWeights, numberOfHeads, Query, Key, Value):
        attentionHeads = np.array(attentionHeads)
        attentionWeights = np.array(attentionWeights)
        attentionHeadGradients, outputWeightGradient, outputBiasGradient = self._outputProjectionLayerBackpropagation(self.embededDimension, batchSize, sequenceLength, outputGradient, attentionHeads, self.outputWeights)
        queryDerivative, keyDerivative, valueDerivative = self._attentionBackpropagation(attentionWeights, numberOfHeads, Query, Key, Value, attentionHeadGradients)
        inputDerivative, QueryWeightDerivative, KeyWeightDerivative, ValueWeightDerivative = self._QKVLinearProjectionBackpropagation(originalInput, queryDerivative, keyDerivative, valueDerivative, self.QueryWeights, self.KeyWeights, self.ValueWeights)
        return outputWeightGradient, outputBiasGradient, inputDerivative, QueryWeightDerivative, KeyWeightDerivative, ValueWeightDerivative

    def _outputProjectionLayerBackpropagation(self, embededDimension, batchSize, sequenceLength, outputGradient, attentionHeads, outputWeights):
        assert outputGradient.shape == (batchSize, sequenceLength, embededDimension), f"outputGradient shape {outputGradient.shape} != expected {(batchSize, sequenceLength, embededDimension)}"
        assert attentionHeads.ndim == 4, f"attentionHeads must be 4D but got {attentionHeads.ndim}D"

        outputWeightGradient = np.zeros((embededDimension, embededDimension))
        for b in range(batchSize):
            for s in range(sequenceLength):
                flattenedAttention = attentionHeads.transpose(1, 2, 0, 3)[b, s].reshape(-1)
                outputWeightGradient += np.outer(flattenedAttention, outputGradient[b, s])
        
        outputBiasGradient = np.sum(outputGradient, axis=(0, 1))
        attentionHeadGradients = np.matmul(outputGradient, outputWeights.T)

        assert outputBiasGradient.shape == (embededDimension,), f"outputBiasGradient shape {outputBiasGradient.shape} != expected {(embededDimension,)}" 
        assert attentionHeadGradients.shape == outputGradient.shape, f"attentionHeadGradients shape {attentionHeadGradients.shape} != expected {outputGradient.shape}"

        return attentionHeadGradients, outputWeightGradient, outputBiasGradient
    
    def _softmaxDerivative(self, output, gradient):
        gradient = output * (gradient - np.sum(gradient * output, axis=-1, keepdims=True))
        return gradient

    def _attentionBackpropagation(self, attentionWeights, numberOfHeads, Query, Key, Value, outputLoss):
        # Attention formula:
        #   score = (Q @ K.T) / sqrt(d)
        #   attention = softmax(score)
        #   output = attention @ V

        # Backprop: ( [L/V] means partial derivative of L with respect to V)
        #   [Loss/Value] = attention @ [Loss/Output]
        #   [Loss/attention] = [Loss/Output] @ V
        #   [Loss/score] = gradient of softmax(attention, [loss/attention])
        #   [Loss/Query] = (1/sqrt(d)) * [Loss/score] @ Key
        #   [Loss/Key] = (1/sqrt(d)) * [Loss/score] @ Query

        if(Query.ndim == 3):
            batchSize, sequenceLength, embdeddedDimension = Query.shape
        elif(Query.ndim == 2):
            sequenceLength, embdeddedDimension = Query.shape
            batchSize = 1
        else:
            raise ValueError(f"Query dimension {Query.ndim}D, expected 3D")
        headDimension = embdeddedDimension // numberOfHeads

        self.batchSize = batchSize
        self.sequenceLength = sequenceLength
        self.embdeddedDimension = embdeddedDimension
        self.numberOfHeads = numberOfHeads

        outputLoss = outputLoss.reshape(batchSize, sequenceLength, numberOfHeads, headDimension).transpose(0, 2, 1, 3)
        assert outputLoss.shape == (batchSize, numberOfHeads, sequenceLength, headDimension), f"Output loss is the wrong shape {outputLoss.shape}, expected {(batchSize, numberOfHeads, sequenceLength, headDimension)}"
        assert attentionWeights.shape == (numberOfHeads, batchSize, sequenceLength, sequenceLength), f"Attention weight is the wrong shape {attentionWeights.shape}, expected {(numberOfHeads, batchSize, sequenceLength, sequenceLength)}"

        # From (seqLen, batchSize, embedDim) to (batchSize, numHeads, seqLen, headDim)
        Q = Query.transpose(1, 0, 2).reshape(batchSize, sequenceLength, numberOfHeads, headDimension).transpose(0, 2, 1, 3)
        K = Key.transpose(1, 0, 2).reshape(batchSize, sequenceLength, numberOfHeads, headDimension).transpose(0, 2, 1, 3)
        V = Value.transpose(1, 0, 2).reshape(batchSize, sequenceLength, numberOfHeads, headDimension).transpose(0, 2, 1, 3)

        valueDerivative = np.matmul(attentionWeights.transpose(1, 0, 3, 2), outputLoss)
        outputLoss = outputLoss.reshape(batchSize, sequenceLength, numberOfHeads, headDimension).transpose(0, 2, 1, 3)
        
        attentionDerivative = np.matmul(outputLoss, V.transpose(0, 1, 3, 2))

        attentionWeights = attentionWeights.transpose(1, 0, 2, 3)
        assert attentionWeights.shape == attentionDerivative.shape, f"Mismatch: attention {attentionWeights.shape}, attentionDerivative {attentionDerivative.shape}"

        scoreDerivative = self._softmaxDerivative(attentionWeights, attentionDerivative)
        
        queryDerivative = (1/np.sqrt(V.shape[-1])) * np.matmul(scoreDerivative, K)
        keyDerivative = (1/np.sqrt(V.shape[-1])) * np.matmul(scoreDerivative.transpose(0, 1, 3, 2), Q)

        return queryDerivative, keyDerivative, valueDerivative
    
    def _QKVLinearProjectionBackpropagation(self, inputToAttentionBlock, queryDerivative, keyDerivative, valueDerivative, QueryWeights, KeyWeights, ValueWeights):
        input = inputToAttentionBlock.transpose(0, 2, 1)
        assert input.shape == (self.batchSize, self.embdeddedDimension, self.sequenceLength), f"Input is the wrong shape {input.shape}, expected {(self.batchSize, self.embdeddedDimension, self.sequenceLength)}"

        b, n, s, h = queryDerivative.shape
        queryDerivative = queryDerivative.transpose(0, 2, 1, 3).reshape(b, s, n * h)
        keyDerivative = keyDerivative.transpose(0, 2, 1, 3).reshape(b, s, n * h)
        valueDerivative = valueDerivative.transpose(0, 2, 1, 3).reshape(b, s, n * h)

        QueryWeightDerivative = np.matmul(input, queryDerivative)
        KeyWeightDerivative = np.matmul(input, keyDerivative)
        ValueWeightDerivative = np.matmul(input, valueDerivative)

        inputQueryDerivative = np.matmul(queryDerivative, QueryWeights.T)
        inputKeyDerivative = np.matmul(keyDerivative, KeyWeights.T)
        inputValueDerivative = np.matmul(valueDerivative, ValueWeights.T)

        inputDerivative = inputQueryDerivative + inputKeyDerivative + inputValueDerivative

        return inputDerivative, QueryWeightDerivative, KeyWeightDerivative, ValueWeightDerivative
