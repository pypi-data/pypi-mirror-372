from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

import torch
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

if TYPE_CHECKING:
    import torch.nn as nn


@dataclass
class TrainerConfig:
    """
    Configuration class for a trainer.

    Attributes:
        device: The device on which to perform training.
        learning_rate: The fixed learning rate to use.
        batch_size: The size of each training batch.
        num_workers: The number of subprocess workers to use for loading data.
        collator: The function to use for batching samples.
        num_samples: The number of samples to use during training.
        max_grad_norm: The max norm to which gradient are clipped.
    """

    device: str = "cpu"
    learning_rate: float = 1e-4
    batch_size: int = 64
    num_workers: int = 0
    collator: Callable | None = None
    num_samples: int = 100_000
    max_grad_norm: float = 1


class Trainer:
    """Simple model-agnostic PyTorch trainer class."""

    def __init__(self, model: nn.Module, config: TrainerConfig):
        self.model = model
        self.config = config
        self.device = config.device

    def run(self, data: Dataset):
        """
        Train the BabyBERT model on the provided dataset.

        Args:
            data: The `Dataset` to use for training.
        """
        model = self.model
        config = self.config

        optimizer = torch.optim.Adam(model.parameters(), config.learning_rate)

        loader = DataLoader(
            data,
            batch_size=config.batch_size,
            num_workers=config.num_workers,
            collate_fn=config.collator,
            sampler=torch.utils.data.RandomSampler(
                data, replacement=True, num_samples=config.num_samples
            ),
        )

        model.train()

        pbar = tqdm(
            loader,
            colour="yellow",
            desc="Training",
            unit="samples",
            unit_scale=config.batch_size,
        )

        for batch in pbar:
            batch = [sample.to(self.device) for sample in batch]
            x, masks, y = batch
            _, loss = model(x, mask=masks, labels=y)

            pbar.set_postfix({"loss": f"{loss:.4f}"})

            optimizer.zero_grad()

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), config.max_grad_norm)
            optimizer.step()
