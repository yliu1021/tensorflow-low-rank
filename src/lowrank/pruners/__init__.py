import enum
from typing import Callable, Optional

import numpy as np
from tensorflow.keras import losses, models

from lowrank.low_rank_layer import LowRankLayer


class PruningScope(enum.Enum):
    GLOBAL = enum.auto()  # global pruning will score all ranks from all layers together
    LOCAL = enum.auto()  # local pruning will treat each layer independently


class Pruner:
    """
    Pruners take a model, and upon examining its effective weights, computes rank masks for
    each layer
    """

    def __init__(
        self,
        model: models.Sequential,
        scope: PruningScope,
        sparsity: float,
        data: Optional[tuple[np.ndarray, np.ndarray]] = None,
        loss: Optional[losses.Loss] = None,
    ):
        self.model = model
        self.scope = scope
        if sparsity < 0 or sparsity > 1:
            raise ValueError("Sparsity must be in the range [0, 1]")
        self.sparsity = sparsity
        self.data = data
        self.loss = loss
        self.low_rank_layers: list[LowRankLayer] = list(
            filter(lambda x: isinstance(x, LowRankLayer), self.model.layers)
        )

    def compute_masks(self) -> list[list[bool]]:
        """
        Computes and returns a list of masks for each layer in the model.
        """
        raise NotImplementedError("Must be called on a subclass of Pruner")

    def prune(self):
        """
        Calls the `compute_mask` method and actually sets the ranks
        """

        for layer in self.low_rank_layers:
            if layer.rank_capacity is None:
                layer.set_rank_capacity(layer.max_rank)
        masks = self.compute_masks()
        if len(masks) != len(self.low_rank_layers):
            raise ValueError("Computed mask does not match length of model layers")
        for mask, layer in zip(masks, self.low_rank_layers):
            assert layer.rank_capacity == len(mask), (
                "Computed mask should be the same length as " "rank capacity"
            )
            layer.set_mask(mask)
            layer.squeeze_rank_capacity()
        self.model._reset_compile_cache()  # ensure model is recompiled
