from typing import Tuple

import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import cifar10, cifar100

Dataset = Tuple[np.ndarray, np.ndarray]


def _normalize_x(x: np.ndarray) -> np.ndarray:
    return x.astype(np.float32) / 255.0


def _one_hot_y(y: np.ndarray) -> np.ndarray:
    num_classes = np.max(y) + 1
    y = np.squeeze(y)
    return np.array(tf.one_hot(y, depth=num_classes))


def _shuffle(label: np.ndarray) -> np.ndarray:
    shuffled_label = np.zeros_like(label)
    while np.sum(shuffled_label) == 0:
        shuffled_label = np.zeros_like(label)
        shuffled_label[np.random.randint(len(label))] = 1
        shuffled_label *= 1 - label
    return shuffled_label


def load_data(dataset: str, noise: float = 0.0) -> Tuple[Dataset, Dataset]:
    """
    Loads a dataset and adds noisy labels to `noise` percent of the training labels
    :param dataset: the dataset to load: "cifar10" or "cifar100"
    :param noise: a number between 0 and 1
    :return: a tuple of Datasets for training and testing
    """
    if dataset == "cifar10":
        load = cifar10.load_data
    elif dataset == "cifar100":
        load = cifar100.load_data
    else:
        raise ValueError(f"Invalid dataset: {dataset}")
    (x_train, y_train), (x_test, y_test) = load()
    if noise < 0 or noise > 1:
        raise ValueError("Noise parameter must be between 0 and 1")
    x_train = _normalize_x(x_train)
    x_test = _normalize_x(x_test)
    y_train = _one_hot_y(y_train)
    y_test = _one_hot_y(y_test)
    num_noisy_labels = int(round(noise * len(y_train)))
    for noisy_index in np.random.choice(len(y_train), size=num_noisy_labels, replace=False):
        y_train[noisy_index] = _shuffle(y_train[noisy_index])
    return (x_train, y_train), (x_test, y_test)
