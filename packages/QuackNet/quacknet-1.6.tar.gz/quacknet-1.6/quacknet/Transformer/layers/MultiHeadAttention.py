from quacknet.Transformer.layers.AttentionBackpropagation import MultiHeadAttentionBackpropagation
import numpy as np

"""
Q = X @ W_Q

W_Q = Weights for query


K = X @ W_K

W_K = Weights for Key


V = X @ W_V

W_V = Weights for Value


a(Q, K, V) = softmax( (Q @ K.T) / sqrt(d) ) @ V 

a = attention
d = dimension of the key vector


O = at @ W_O + W_B

O = output
at = combined attention
W_O = output projection weight
W_O = output projection bias

Q = Query
K = Key
V = Value
X = Input embedding
@ = matrix multiplication

Order of forward prop:
-   QKV Linear projection (get QKV)
-   Split into heads (divide QKV)
-   Compute attention per Head
-   Combine all the attention 
-   Output linear projection (basically a dense layer but for 3D tensor)
"""

class MultiAttentionHeadLayer:
    def __init__(self, batchSize, sequenceLength, embedDimension, numberOfHeads, QueryWeights, KeyWeights, ValueWeights, outputWeight, outputBias, useCasualMasking = False):
        self.embedDimension = embedDimension
        self.numberOfHeads = numberOfHeads
        self.QueryWeights = QueryWeights
        self.KeyWeights = KeyWeights
        self.ValueWeights = ValueWeights
        self.outputWeight = outputWeight
        self.outputBias = outputBias
        self.batchSize = batchSize 
        self.sequenceLength = sequenceLength
        self.useCasualMasking = useCasualMasking
        if(self.useCasualMasking == True):
            self.casualMask = self.createCausalMask(batchSize, sequenceLength)

        assert embedDimension % numberOfHeads == 0, "Embedding Dimension must be divisible by the number of heads"

        self.createWeights()

        self.backProp = MultiHeadAttentionBackpropagation(
            embededDimension=embedDimension,
            outputWeights=self.outputWeight,
            QueryWeights=self.QueryWeights,
            KeyWeights=self.KeyWeights,
            ValueWeights=self.ValueWeights
        )

    def QKVLinearProjection(self, inputEmbedding):
        self.Query = inputEmbedding @ self.QueryWeights
        self.Key = inputEmbedding @ self.KeyWeights
        self.Value = inputEmbedding @ self.ValueWeights
        return self.Query, self.Key, self.Value
    
    def SplitIntoHeads(self, Query, Key, Value):
        # QVK has a shape of (batchSize, sequenceLength, embedDimension)
        headDimension = self.embedDimension // self.numberOfHeads # // returns a whole number (floor division)

        # reshape to split heads
        QReshaped = Query.reshape(self.batchSize, self.sequenceLength, self.numberOfHeads, headDimension)
        KReshaped = Key.reshape(self.batchSize, self.sequenceLength, self.numberOfHeads, headDimension)
        VReshaped = Value.reshape(self.batchSize, self.sequenceLength, self.numberOfHeads, headDimension)
        
        # Transpose to (batchSize, numberHeads, sequenceLength, headDimension)
        QHead = QReshaped.transpose(0, 2, 1, 3)
        KHead = KReshaped.transpose(0, 2, 1, 3)
        VHead = VReshaped.transpose(0, 2, 1, 3)

        return QHead, KHead, VHead
    
    def _TransformerSoftMax(self, values): # softmax in quacknet.core works for 1D arrays not 3D/4D tensors
        values = np.array(values, dtype=np.float64)
        maxVal = np.max(values, axis=-1, keepdims=True)
        values = values - maxVal
        summ = np.sum(np.exp(values), axis=-1, keepdims=True)
        out = np.exp(values) / summ
        return out

    def _calculateAttentionForOneHead(self, QueryHead, KeyHead, ValueHead):
        # a(Q, K, V) = softmax( (Q @ K.T) / sqrt(d) ) @ V 
        attentionScore = (QueryHead @ KeyHead.transpose(0, 2, 1)) / np.sqrt(ValueHead.shape[1])
        
        if(self.useCasualMasking == True):
            attentionScore = np.where(self.casualMask == 0, -1e9, attentionScore) # masks attention with very large negative number 
        
        attentionWeights = self._TransformerSoftMax(attentionScore)  # this is used in backprop
        attentionOutput = attentionWeights @ ValueHead
        return attentionOutput, attentionWeights

    def calculateAttention(self, QueryHead, KeyHead, ValueHead):
        self.attentionHeads = []
        self.attentionWeights = []
        for i in range(self.numberOfHeads):
            att, att_W = self._calculateAttentionForOneHead(
                QueryHead[:, i, :, :],
                KeyHead[:, i, :, :], 
                ValueHead[:, i, :, :],
            )
            self.attentionHeads.append(att)
            self.attentionWeights.append(att_W)
            
        stackedHeads = np.stack(self.attentionHeads, axis=1)
        stackedHeads = np.transpose(stackedHeads, (0, 2, 1, 3))
        batchSize, sequenceLength, numberHeads, headDimension = stackedHeads.shape
        combinedAttention = stackedHeads.reshape(batchSize, sequenceLength, numberHeads * headDimension)
        return combinedAttention
        
    def outputProjectionLayer(self, combinedAttention):
        output = combinedAttention @ self.outputWeight + self.outputBias
        return output
    
    def forwardPropagation(self, inputEmbedding):
        if(inputEmbedding.ndim == 2):
            inputEmbedding = inputEmbedding[np.newaxis, :, :]
        self.originalInput = inputEmbedding # for backprop
        Query, Key, Value = self.QKVLinearProjection(inputEmbedding)
        QHead, KHead, VHead = self.SplitIntoHeads(Query, Key, Value)
        combinedAttention = self.calculateAttention(QHead, KHead, VHead)
        output = self.outputProjectionLayer(combinedAttention)
        return output
    
    def createWeights(self):
        self.QueryWeights = self._initiaseWeight(self.embedDimension, self.embedDimension)
        self.KeyWeights = self._initiaseWeight(self.embedDimension, self.embedDimension)
        self.ValueWeights = self._initiaseWeight(self.embedDimension, self.embedDimension)
        self.outputWeight = self._initiaseWeight(self.embedDimension, self.embedDimension)
        self.outputBias = np.zeros((1, self.embedDimension))

    def _initiaseWeight(self, inputDimension, outputDimension):
        return np.random.rand(inputDimension, outputDimension) * (1 / np.sqrt(inputDimension))
    
    def backwardPropagation(self, outputGradient):
        outputWeightGradient, outputBiasGradient, inputDerivative, QueryWeightDerivative, KeyWeightDerivative, ValueWeightDerivative = self.backProp.backPropagation(
            originalInput=self.originalInput,
            batchSize=self.batchSize,
            sequenceLength=self.sequenceLength,
            outputGradient=outputGradient,
            attentionHeads=self.attentionHeads,
            attentionWeights=self.attentionWeights,
            numberOfHeads=self.numberOfHeads,
            Query=self.Query,
            Key=self.Key,
            Value=self.Value
        )
        return outputWeightGradient, outputBiasGradient, inputDerivative, QueryWeightDerivative, KeyWeightDerivative, ValueWeightDerivative
    
    def createCausalMask(self, batchSize, sequenceLength):
        mask = np.tril(np.ones((sequenceLength, sequenceLength), dtype=np.bool_))
        mask = mask[np.newaxis, :, :]
        mask = np.repeat(mask, batchSize, axis=0)
        return mask