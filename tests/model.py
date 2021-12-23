from tensorflow.keras.layers import (
    AveragePooling2D,
    Conv2D,
    Dense,
    Flatten,
    InputLayer,
    MaxPool2D,
)
from tensorflow.keras.models import Sequential

from lowrank import LRDense, LRConv2D


def get_model(input_shape: list[int], num_classes: int, rank: int):
    return Sequential(
        [
            InputLayer(input_shape=input_shape),
            Conv2D(64, 3, activation="relu", padding="same"),
            MaxPool2D(),
            Conv2D(128, 3, activation="relu", padding="same"),
            MaxPool2D(),
            Conv2D(256, 3, activation="relu", padding="same"),
            MaxPool2D(),
            Conv2D(512, 3, activation="relu", padding="same"),
            AveragePooling2D(),
            Flatten(),
            LRDense(256, rank=rank, activation="relu"),
            Dense(num_classes, activation="softmax"),
        ]
    )


def get_lr_conv_model(input_shape: list[int], num_classes: int, rank: int):
    return Sequential(
        [
            InputLayer(input_shape=input_shape),
            LRConv2D(64, 3, rank=32, activation="relu", padding="same"),
            MaxPool2D(),
            LRConv2D(128, 3, rank=64, activation="relu", padding="same"),
            MaxPool2D(),
            LRConv2D(256, 3, rank=64, activation="relu", padding="same"),
            MaxPool2D(),
            LRConv2D(512, 3, rank=32, activation="relu", padding="same"),
            AveragePooling2D(),
            Flatten(),
            LRDense(256, rank=rank, activation="relu"),
            Dense(num_classes, activation="softmax"),
        ]
    )
