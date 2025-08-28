"""
This is like a central class which makes it easier to turn on/off debugs and reduces
the amount of asserts i have to write
"""

class checker:
    def __init__(self, enabled=True):
        self.enabled = enabled
    
    def checkShape(self, actualShape, expectedShape, msg=None):
        if(self.enabled == False):
            return
        if(actualShape != expectedShape):
            if(msg is None):
                msg = f"Shape mismatch: got {actualShape}, expected {expectedShape}"
            raise AssertionError(msg)
        
    def checkEqual(self, actual, expected, msg=None):
        if(self.enabled == False):
            return
        if(actual != expected):
            if(msg is None):
                msg = f"Value mismatch: got {actual}, expected {expected}"
            raise AssertionError(msg)
    
    def checkSize(self, actualSize, expectedSize, msg=None):
        if(self.enabled == False):
            return
        if(actualSize != expectedSize):
            if(msg is None):
                msg = f"Value mismatch: got {actualSize}, expected {expectedSize}"
            raise AssertionError(msg)
    
    def checkTrue(self, condition, msg=None):
        if(self.enabled == False):
            return
        if(condition == False):
            if(msg is None):
                msg = f"Condition failed"
            raise AssertionError(msg)

globalChecker = checker(enabled=True)

def setCheckEnabled(enabled):
    globalChecker.enabled = enabled