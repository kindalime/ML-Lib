import tensorflow as tf
from math import prod
from .base import Layer


class FlattenLayer(Layer):
    def __init__(self):
        super().__init__()
        
    def __str__(self):
        return "Flatten Layer"

    def __repr__(self):
        return "FlattenLayer()"

    def set_dims(self, inp):
        self.inp = inp
        self.out = [prod(inp)]

    def op(self, X):
        return tf.reshape(X, [X.shape[0], prod(X.shape[1:])])
