from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

import torch
import torch.nn as nn
import torch.nn.functional as F

from babybert.utils import resolve_checkpoint_path


@dataclass
class BabyBERTConfig:
    """
    Configuration class for BabyBERT.

    Attributes:
        vocab_size: The vocab size of the tokenizer used to create inputs.
        block_size: The length of the input sequences.
        hidden_size: The size of the model's hidden states. Must be divisible by
                     `n_heads`.
        n_blocks: The number of transformer blocks to use.
        n_heads: The number of attention heads to use.
        attention_dropout_probability: The dropout probability for the output of each
                                       attention head.
        attention_projection_dropout_probability: The dropout probability for the
                                                  output projection of a multi-head
                                                  self-attention block.
        mlp_dropout_probability: The dropout probability for the MLP used for tokenwise
                                 learning.
        embedding_dropout_probability: The dropout probability for input sequence
                                       embeddings.
    """

    vocab_size: int
    block_size: int
    hidden_size: int = 768
    n_blocks: int = 12
    n_heads: int = 12
    attention_dropout_probability: float = 0.1
    attention_projection_dropout_probability: float = 0.1
    mlp_dropout_probability: float = 0.1
    embedding_dropout_probability: float = 0.1
    ignore_index: int = -100

    _PRESETS: ClassVar[dict[str, dict]] = {
        "tiny": {
            "hidden_size": 128,
            "n_blocks": 2,
            "n_heads": 2,
        },
        "small": {
            "hidden_size": 256,
            "n_blocks": 4,
            "n_heads": 4,
        },
        "base": {
            "hidden_size": 768,
            "n_blocks": 12,
            "n_heads": 12,
        },
    }

    @classmethod
    def from_preset(cls, name: str, **kwargs) -> BabyBERTConfig:
        """
        Load a configuration object from a preset.

        **Note**: The configuration presets only contain values for `hidden_size`,
        `n_blocks`, and `n_heads`. Other required attributes without defaults, such as
        `vocab_size` and `block_size`, must be passed in as keyword arguments to this
        method. Keyword arguments with defaults can optionally be included as well.

        **Available presets**:
        - `"tiny"`: `hidden_size=128`, `n_blocks=2`, `n_heads=2`
        - `"small"`: `hidden_size=256`, `n_blocks=4`, `n_heads=4`
        - `"base"`: `hidden_size=768`, `n_blocks=12`, `n_heads=12`

        Args:
            name: The name of the configuration preset from which to load.
        Returns:
            A new configuration object, with values populated by the defaults.
        """
        if name not in cls._PRESETS:
            available = ", ".join(f"'{key}'" for key in cls._PRESETS.keys())
            raise ValueError(
                f"Preset config '{name}' is not available."
                f"Available presets: {available}"
            )
        return cls(**cls._PRESETS[name], **kwargs)


class AttentionHead(nn.Module):
    """Implementation of a single self-attention head."""

    def __init__(self, config: BabyBERTConfig):
        super().__init__()

        # The size of each attention head's latent space is equal to the embedding
        # space's size divided by the number of heads. That way, after we compute the
        # context vector for each attention head, we can concatenate them to produce a
        # vector that's the same size as the original embedding space.
        head_size = config.hidden_size // config.n_heads

        # Layers for projecting the input embeddings into three spaces:
        # the query (Q) space, the key (K) space, and the value (V) space.
        self.query_embedding = nn.Linear(config.hidden_size, head_size)
        self.key_embedding = nn.Linear(config.hidden_size, head_size)
        self.value_embedding = nn.Linear(config.hidden_size, head_size)

        self.dropout = nn.Dropout(config.attention_dropout_probability)

    def forward(self, x, mask=None):
        # Project the inputs into each space.
        q = self.query_embedding(x)
        k = self.key_embedding(x)
        v = self.value_embedding(x)

        # Perform scaled dot product attention (SDPA) using the query and key matrices
        # - this yields the similarity between each embedding in our input sequences.
        raw_attention_weights = (q @ torch.transpose(k, -2, -1)) / math.sqrt(q.size(-1))

        # If we have an attention mask, we replace each of the masked tokens with a
        # negative infinity in our attention weight matrix. This makes sure that the
        # attention score will be 0 when we compute the softmax later.
        if mask is not None:
            mask = mask.unsqueeze(1)
            raw_attention_weights = raw_attention_weights.masked_fill(
                mask == 0, float("-inf")
            )

        # Compute the softmax over each input sequence, normalizing the scores.
        normalized_attention_weights = F.softmax(raw_attention_weights, -1)
        normalized_attention_weights = self.dropout(normalized_attention_weights)

        # Taking the dot product of the weight matrix and the value matrix gives us our
        # final context vector.
        context_vector = normalized_attention_weights @ v

        return context_vector


class MultiHeadSelfAttention(nn.Module):
    """Implementation of a multi-head self-attention layer."""

    def __init__(self, config: BabyBERTConfig):
        super().__init__()

        # Initialize n attention heads - this allows us to capture n sets of
        # relationships between token embeddings.
        self.attention_heads = nn.ModuleList(
            [AttentionHead(config) for _ in range(config.n_heads)]
        )
        self.output_projection = nn.Linear(config.hidden_size, config.hidden_size)
        self.dropout = nn.Dropout(config.attention_projection_dropout_probability)

    def forward(self, x, mask=None):
        # Concatenate the output of each of the n attention heads.
        x = torch.cat(
            [attention_head(x, mask) for attention_head in self.attention_heads], dim=-1
        )

        # Project the concatenated vectors to the output space.
        x = self.output_projection(x)
        x = self.dropout(x)
        return x


class TransformerBlock(nn.Module):
    """Implementation of a transformer block."""

    def __init__(self, config: BabyBERTConfig):
        super().__init__()

        self.mhsa = MultiHeadSelfAttention(config)
        self.layer_norm_1 = nn.LayerNorm(config.hidden_size)

        # Simple multilayer perceptron (MLP) to handle tokenwise learning.
        self.mlp = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size * 4),
            nn.GELU(),
            nn.Linear(config.hidden_size * 4, config.hidden_size),
            nn.Dropout(config.mlp_dropout_probability),
        )
        self.layer_norm_2 = nn.LayerNorm(config.hidden_size)

    def forward(self, x, mask=None):
        # Pass the input through our multi-head self attention layer.
        x = x + self.mhsa(x, mask)
        x = self.layer_norm_1(x)

        # Pass the input through the MLP.
        x = x + self.mlp(x)
        x = self.layer_norm_2(x)
        return x


class BabyBERT(nn.Module):
    """Minimal implementation of [BERT](https://arxiv.org/pdf/1810.04805)."""

    def __init__(self, config: BabyBERTConfig):
        super().__init__()

        self.config = config

        # Learned embeddings for each token ID in the vocabulary.
        self.token_embeddings = nn.Embedding(config.vocab_size, config.hidden_size)

        # Learned embeddings for each segment; we only have segments 1 and 2 in BERT.
        self.segment_embeddings = nn.Embedding(2, config.hidden_size)

        # Learned embeddings for each token position.
        # Having positional embeddings is necessary for the model to understand the
        # order of the input tokens.
        self.positional_embeddings = nn.Embedding(config.block_size, config.hidden_size)

        self.dropout = nn.Dropout(config.embedding_dropout_probability)
        self.transformer_blocks = nn.ModuleList(
            [TransformerBlock(config) for _ in range(config.n_blocks)]
        )

    def forward(self, token_ids, attention_mask=None, segment_encodings=None):
        # Get the position IDs - these range from 0 to the max length of an input
        # sequence (stored in the block_size variable).
        position_ids = torch.arange(
            0, self.config.block_size, device=token_ids.device
        ).unsqueeze(0)

        # If no segment encodings tensor was passed in, assume everything belongs
        # to the first segment (represented by '0')
        if segment_encodings is None:
            segment_encodings = torch.zeros_like(token_ids)

        # Sum the token, segment, and positional embeddings to obtain the complete
        # embedding tensor.
        x = self.token_embeddings(token_ids)
        x = x + self.segment_embeddings(segment_encodings)
        x = x + self.positional_embeddings(position_ids)

        x = self.dropout(x)

        # Pass the embeddings through each transformer block in our model.
        for block in self.transformer_blocks:
            x = block(x, attention_mask)

        return x

    @classmethod
    def from_pretrained(cls, name: str | Path) -> BabyBERT:
        """
        Loads a pretrained `BabyBERT` model from a directory. The directory should
        contain a file named `config.json`, which stores the configuration settings,
        and a file named `pytorch_model.bin`, which contains the model weights.

        Args:
            name: The directory containing the `BabyBERT` model configuration settings
                  and weights.
        Returns:
            An instance of `BabyBERT` with configuration settings and weights loaded
            from the input directory.
        """
        name = resolve_checkpoint_path(name)

        with open(name / "config.json", "r") as config_file:
            config_dict = json.load(config_file)
        config = BabyBERTConfig(**config_dict)

        model = cls(config)

        state_dict = torch.load(name / "pytorch_model.bin", weights_only=True)
        model.load_state_dict(state_dict)

        return model

    def save_pretrained(self, name: str | Path) -> None:
        """
        Saves a pretrained `BabyBERT` model in a directory for later use. Creates two
        new files in the directory: one called `config.json`, which contains
        configuration settings, and another called `pytorch_model.bin`, which contains
        the model weights.

        Args:
            name: The directory in which to save the model's configuration settings and
                  weights.
        """
        name = Path(name)
        name.mkdir(parents=True, exist_ok=True)

        with open(name / "config.json", "w") as config_file:
            json.dump(self.config.__dict__, config_file)

        torch.save(self.state_dict(), name / "pytorch_model.bin")


class BabyBERTForMLM(nn.Module):
    """BabyBERT model with added masked language modeling (MLM) head."""

    def __init__(self, bert: BabyBERT):
        super().__init__()

        self.bert = bert
        self.config = self.bert.config

        # Projection from each BabyBERT contextual embedding to the vocabulary space.
        self.mlm_head = nn.Linear(self.config.hidden_size, self.config.vocab_size)

    def forward(self, token_ids, attention_mask=None, labels=None):
        x = self.bert(token_ids, attention_mask)

        # Obtain the logits for each contextual embedding - we'll only use the logits
        # from the [MASK] tokens.
        mlm_logits = self.mlm_head(x)

        loss = None

        if labels is not None:
            # Flatten the logit and label vectors, rendering them suitable inputs for
            # PyTorch's cross entropy loss function.
            flattened_logits = mlm_logits.view(-1, mlm_logits.size(-1))
            flattened_labels = labels.view(-1)

            # Here's where the important stuff happens - at each masked position in
            # the input sequence, we compare the predicted token probabilities to
            # the true token IDs. If they match up, we have a low loss value; if
            # they're substantially different, our loss will be higher.
            loss = F.cross_entropy(
                flattened_logits,
                flattened_labels,
                ignore_index=self.config.ignore_index,
            )

        return mlm_logits, loss


class BabyBERTForSentimentClassification(nn.Module):
    """BabyBERT model with added sentiment classification head."""

    def __init__(self, bert: BabyBERT):
        super().__init__()

        self.bert = bert
        self.config = self.bert.config

        # Projection from each BabyBERT classification token embedding to a predicted
        # sentiment score (positive or negative)
        self.sentiment_classification_head = nn.Linear(self.config.hidden_size, 2)

    def forward(self, token_ids, attention_mask=None, labels=None):
        x = self.bert(token_ids, attention_mask)

        # Obtain the [CLS] token embedding from each sequence in the batch.
        cls_embeddings = x[:, 0, :]

        # Use our sentiment analysis head to predict a probability for each sentiment
        # class using the [CLS] embedding.
        sentiment_scores = self.sentiment_classification_head(cls_embeddings)

        loss = None

        if labels is not None:
            # Calculate the difference between the class predictions and the ground
            # truth label
            loss = F.cross_entropy(input=sentiment_scores, target=labels)

        return sentiment_scores, loss
