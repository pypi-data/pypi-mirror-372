
class ResidualConnection:
    #output being the output of the layer before
    def forwardPropagation(self, input, output): # input being the input of the layer before
        return input + output # y = x + f(x)