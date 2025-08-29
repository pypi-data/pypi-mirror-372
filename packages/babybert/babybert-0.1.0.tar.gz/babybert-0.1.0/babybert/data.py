from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

import torch
from torch.utils.data import Dataset

if TYPE_CHECKING:
    from tokenizer import WordPieceTokenizer


class LanguageModelingDataset(Dataset):
    """Class for storing an LM dataset."""

    def __init__(
        self,
        token_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: list[int] | torch.Tensor | None = None,
    ):
        self.token_ids = token_ids
        self.attention_mask = attention_mask
        self.labels = torch.tensor(labels) if labels else None

    def __len__(self) -> int:
        return len(self.token_ids)

    def __getitem__(
        self, index: int
    ) -> (
        tuple[torch.Tensor, torch.Tensor, torch.Tensor]
        | tuple[torch.Tensor, torch.Tensor]
    ):
        if self.labels is not None:
            return self.token_ids[index], self.attention_mask[index], self.labels[index]
        else:
            return self.token_ids[index], self.attention_mask[index]

    @property
    def seq_length(self) -> int:
        """Returns the length of the sequences in the dataset."""
        return self.token_ids.size(1)

    @classmethod
    def from_dict(cls, data: dict[str, torch.Tensor]) -> LanguageModelingDataset:
        """
        Create a new dataset instance from a dictionary.

        Args:
            data: A dictionary containing entries `token_ids`, `attention_mask`, and
                  optionally `labels`.
        Returns:
            A new dataset object with values populated from the dictionary.
        """
        return cls(
            data.get("token_ids"), data.get("attention_mask"), data.get("labels")
        )


class CollatorForMLM:
    """Data collator for applying masks to batches of tokens."""

    def __init__(
        self,
        tokenizer: WordPieceTokenizer,
        mask_prob: float = 0.1,
        ignore_index: int = -100,
    ):
        self.tokenizer = tokenizer
        self.mask_prob = mask_prob
        self.ignore_index = ignore_index

    def __call__(
        self, batch: list[tuple[torch.Tensor, torch.Tensor]]
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Perform collation and masking on the input batch.

        Args:
            batch: The batch of tokens to collate and mask.
        Returns:
            The masked token IDs, the attention mask, and the labels for masked tokens.
        """
        token_ids, attention_mask = zip(*batch)

        batched_token_ids = torch.stack(token_ids)
        batched_attention_mask = torch.stack(attention_mask)

        masked_token_ids, labels = self._mask_tokens(batched_token_ids)

        return masked_token_ids, batched_attention_mask, labels

    def _mask_tokens(
        self, token_ids: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Masks tokens in a batch of token IDs, returning the masked input sequence and
        the labels.

        Args:
            token_ids: The batch of token IDs to mask.
        Returns:
            The tensor containing the batch of token IDs after performing masking and
            the tensor containing the labels (-100 for unmasked tokens).
        """
        # This is where we generate the MLM mask. We begin by generating a random value
        # between 0 and 1 for each token ID in the batch. Then, each random value below
        # our masking probability value becomes a masked token (a `True` in the mask),
        # and all other remain unmasked (a `False` in the mask).
        probs = torch.rand_like(token_ids, dtype=torch.float32)
        mlm_mask = probs < self.mask_prob

        # We also want to make sure that we don't accidentally mask a special token;
        # our model doesn't need to know how to predict a padding token! To do this,
        # we create another mask for special tokens.
        special_tokens_mask = ~torch.isin(
            token_ids,
            torch.tensor(self.tokenizer.special_token_ids, device=token_ids.device),
        )

        # We combine our MLM and special tokens masks together to form our final mask.
        mask = mlm_mask & special_tokens_mask

        # Finally, we perform the masking: all tokens selected for masking are replaced
        # with "[MASK]".
        masked_token_ids = token_ids.masked_fill(mask, self.tokenizer.mask_token_id)

        # We only want labels for the masked tokens, as that's what we're trying to
        # predict during training. All other tokens are set to the ignore index in the
        # label tensor (and consequently ignored by our loss function.)
        labels = token_ids.masked_fill(~mask, self.ignore_index)
        return masked_token_ids, labels


def load_corpus(path: str | Path) -> list[str]:
    """
    Loads a corpus from a `.txt` file. Assumes that each sentence is separated by a
    newline.

    Args:
        path: The path to the `.txt` file containing the corpus.
    Returns:
        A `list[str]` containing each sentence from the corpus.
    """
    path = Path(path)
    return path.read_text().split("\n")


def load_dataset(path: str | Path) -> dict[str, list[str] | list[int]]:
    """
    Loads a dataset from a `.txt` file.

    Args:
        path: The path to the `.txt` file containing the dataset. The contents of
              the file should be of the following form:

              ```
              <text 1>
              <integer label for text 1>
              <text 2>
              <integer label for text 2>
              ...
              ```
    Returns:
        A new dataset object with values populated from the text file.
    """
    lines = load_corpus(path)

    if len(lines) % 2 != 0:
        raise ValueError(
            f"The file '{path}' contains an invalid dataset. Make sure that your"
            "file contains alternating lines of texts and labels."
        )

    data_dict = defaultdict(list)
    for text, label in zip(lines[::2], lines[1::2]):
        data_dict["text"].append(text)
        data_dict["label"].append(int(label))
    return dict(data_dict)
