from .tf_model import TFModel
import tensorflow as tf
from utils.compress import *

def logreg(X, w, b):
    return softmax(tf.matmul(X, w) + b)

def softmax(o):
    o_exp = tf.math.exp(o)
    sums = tf.math.reduce_sum(o_exp, 1, keepdims=True)
    return o_exp / sums

def sgd(params, grads, lr, batch_size):
    for param, grad in zip(params, grads):
        param.assign_sub(lr * grad / batch_size)
    
def accuracy(true, pred):
    maxes = tf.math.argmax(pred, axis=1)
    cmp = (tf.cast(maxes, true.dtype) == true)
    return float(tf.reduce_sum(tf.cast(cmp, true.dtype))) / len(pred)

class LogisticModel(TFModel):
    def __init__(self):
        super().__init__()

    def __str__(self):
        s = "Logistic Model\n"
        if self.model_fit:
            s += "Currently fit\n"
            s += f"w.shape: {self.w.shape[0]}\n"
            s += f"classes: {self.classes}\n"
            s += f"loss: {self.loss}\n"
            s += f"lr: {self.lr}\n"
            s += f"epochs: {self.num_epochs}/{self.curr_epoch}\n"
            s += f"update: {self.update}\n"
        else:
            s += "Currently not fit\n"
        return s

    def __repr__(self):
        if self.model_fit:
            s = f"LogisticModel(model_fit={False})"
        else:
            s = f"LogisticModel(model_fit={True}, w={self.w}, b={self.b}, classes={self.classes}, loss={self.loss}, lr={self.lr}, batch_size={self.batch_size}, num_epochs={self.num_epochs}, curr_epoch={self.curr_epoch}, model={self.model}, update={self.update})"
        return s

    def save(self, path):
        super().save()
        data = {
            "loss": self.loss,
            "lr": self.lr,
            "classes": self.classes,
            "batch_size": self.batch_size,
            "num_epochs": self.num_epochs,
            "curr_epoch": self.curr_epoch,
            "model": self.model,
            "update": self.update,
        }
        arrays = {
            "w": self.w,
            "b": self.b,
        }
        compress_files(path, data, arrays)

    def load(self, path):
        data, arrays = uncompress_files(path)
        self.loss = data["loss"]
        self.lr = data["lr"]
        self.num_epochs = data["num_epochs"]
        self.curr_epoch = data["curr_epoch"]
        self.model = data["model"]
        self.update = data["update"]
        self.classes = data["classes"]
        self.w = arrays["w"]
        self.b = arrays["b"]
        
    def validate_fit(self, X, y, classes):
        if X.shape[0] != y.shape[0]:
            raise ValueError("")
        if sorted(tf.unique(y)[0].numpy()) != list(range(0, classes)):
            raise ValueError("")

    def validate_predict(self, X):
        if X.shape[1] != self.w.shape[0]:
            raise ValueError("")

    def build_model(self, w_size, w_classes, w_mean, w_stddev):
        self.w = tf.Variable(tf.random.normal(shape=(w_size, w_classes), mean=w_mean, stddev=w_stddev), trainable=True)
        self.b = tf.Variable(tf.zeros(w_classes), trainable=True)
        self.model = logreg
        self.update = sgd

    def fit(self, X, y, classes, loss, lr=0.03, batch_size=16, num_epochs=32, mean=0, stddev=0.01):
        self.batch_size = batch_size
        self.num_epochs = num_epochs
        self.loss = loss.compare
        self.lr = lr
        self.X = X
        self.y = y
        self.classes = classes
        self.build_model(X.shape[1], classes, mean, stddev)
        self.validate_fit(self.X, self.y, classes)
        super().fit()

    def train_epoch(self):
        for X, y in self.data_iter(self.X, self.y):
            self.train_step(X, y)
        train_l = self.loss(self.y, self.model(self.X, self.w, self.b))
        print(f"epoch {self.curr_epoch}, loss {float(tf.reduce_mean(train_l)):f}, accuracy {float(accuracy(self.y, self.model(self.X, self.w, self.b)))}")

    def train_step(self, X, y):
        with tf.GradientTape() as g:
            l = self.loss(y, self.model(X, self.w, self.b))
        dw, db = g.gradient(l, [self.w, self.b])
        self.update([self.w, self.b], [dw, db], self.lr, self.batch_size)

    def predict(self, X):
        return self.model(X, self.w, self.b)