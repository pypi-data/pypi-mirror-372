import torch

from babybert.model import BabyBERT, BabyBERTConfig


def test_forward_pass():
    config = BabyBERTConfig(
        vocab_size=5,
        hidden_size=10,
        block_size=5,
        n_blocks=1,
        n_heads=10,
        attention_dropout_probability=0.1,
        attention_projection_dropout_probability=0.1,
        mlp_dropout_probability=0.1,
        embedding_dropout_probability=0.1,
    )

    input = torch.asarray([[1, 2, 0, 4, 3], [1, 2, 0, 3, 4]])
    model = BabyBERT(config)
    output = model(input)
    assert output.shape == (2, 5, 10)
