from abc import abstractmethod
import tensorflow as tf
from ..base import Layer


class CoreLayer(Layer):
    def __init__(self, act, reg, param):
        super().__init__()
        self.w = None
        self.b = None
        self.weighted = True
        self.act = act
        self.reg = reg
        self.param = param
        self.initialized = False

    def apply_grad(self, grads):
        for param, grad in zip([self.w, self.b], grads):
            param.assign_sub(param, grad)

    def weights(self):
        return [self.w, self.b]

    def op(self, X):
        if not self.act:
            return self.call(X)
        else:
            return self.act(self.call(X))

    def loss(self):
        if not self.reg:
            return 0
        else:
            return self.reg(self.w)

    def prep_save(self):
        data = [self.w, self.b]
        self.w = None
        self.b = None
        return data

    def finish_save(self, data):
        self.w, self.b = data

    @abstractmethod
    def init_weights(self):
        self.initialized = True

    @abstractmethod
    def call(self, X):
        pass
