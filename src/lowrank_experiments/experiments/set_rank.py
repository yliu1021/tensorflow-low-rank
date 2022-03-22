import datetime
import pathlib

from tensorflow.keras import losses, metrics, optimizers, callbacks

import lowrank.pruners
import lowrank_experiments.data
import lowrank_experiments.model
from lowrank.pruners import alignment_pruner, mag_pruner


def main(dataset: str, sparsity: float, prune_epoch: int, total_epochs: int):
    tensorboard_log_dir = pathlib.Path("./logs_set_rank")
    tensorboard_log_dir.mkdir(exist_ok=True)  # make root logging directory
    tensorboard_log_dir /= "logs_" + datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    (x_train, y_train), (x_test, y_test) = lowrank_experiments.data.load_data(dataset)
    model = lowrank_experiments.model.get_lr_model(
        x_train.shape[1:],
        num_classes=y_train.shape[1],
        initial_ranks=[-1, -1, -1, -1, -1],  # start full rank
    )
    model.compile(
        optimizer=optimizers.RMSprop(0.001),
        loss=losses.CategoricalCrossentropy(),
        metrics=[metrics.CategoricalAccuracy()],
    )
    model.fit(
        x_train,
        y_train,
        batch_size=128,
        epochs=prune_epoch,
        validation_data=(x_test, y_test),
        callbacks=[callbacks.TensorBoard(log_dir=tensorboard_log_dir)]
    )
    print("Before pruning:")
    model.evaluate(x_test, y_test)
    pruner = mag_pruner.MagPruner(
        model, lowrank.pruners.PruningScope.LOCAL, sparsity=sparsity
    )
    pruner.prune()
    print("After pruning")
    model.evaluate(x_test, y_test)
    model.fit(
        x_train,
        y_train,
        batch_size=128,
        epochs=total_epochs,
        validation_data=(x_test, y_test),
        initial_epoch=prune_epoch,
        callbacks=[callbacks.TensorBoard(log_dir=tensorboard_log_dir)]
    )


if __name__ == "__main__":
    main(dataset="cifar10", sparsity=0.3, prune_epoch=5, total_epochs=10)
