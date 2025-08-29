from __future__ import annotations

import json
import re
import warnings
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import torch

from babybert.utils import resolve_checkpoint_path


@dataclass
class TokenizerConfig:
    """
    Configuration class for a tokenizer.

    Attributes:
        _special_tokens: A list of all special tokens that's down have their own
                         attributes.
        padding_token: The token used for padding sequences to a specified length.
        unknown_token: The token used for representing words or subwords outside of the
                       tokenizer's vocabulary.
        mask_token: The token used for masking sequences during masked language
                    modeling.
        classification_token: The token used for downstream classification tasks.
        target_vocab_size: The vocab size that the tokenizer should attempt to reach.
                           If the corpus used for training is too small, it is possible
                           that the vocab of the tokenizer may not reach this size.
    """

    _special_tokens: list[str] = field(default_factory=lambda: ["[SEP]"])
    padding_token: str = "[PAD]"
    unknown_token: str = "[UNK]"
    mask_token: str = "[MASK]"
    cls_token: str = "[CLS]"
    target_vocab_size: int = 1000

    @property
    def special_tokens(self):
        return [
            *self._special_tokens,
            self.padding_token,
            self.unknown_token,
            self.mask_token,
            self.cls_token,
        ]


class WordPieceTokenizer:
    """Basic implementation of WordPiece tokenizer."""

    def __init__(self, config: TokenizerConfig = None):
        self.config = config or TokenizerConfig()
        self.vocab = []

    @staticmethod
    def _pretokenize(text: str) -> list[str]:
        """
        Perform pretokenization on a text. Carries out the following steps:

        - Converts the text to lowercase.
        - Splits on and removes whitespaces.
        - Splits on and preserves punctuation.

        Args:
            text: The text to pretokenize.
        Returns:
            A list containing each part of the pretokenized text.

        Example:
            >>> WordPieceTokenizer._pretokenize("Hello, world!")
            ["hello", ",", "world", "!"]
        """
        text_lower = text.lower()
        parts = re.split(r"\s|([.!?,;])", text_lower)
        return [part for part in parts if part]

    @staticmethod
    def _score_pair(
        first_token: str, second_token: str, pair_freq: int, token_freqs: dict[str, int]
    ) -> float:
        """
        Computes the WordPiece score of a pair of tokens using the following
        formula:

        score = frequency(pair) / (frequency(first) * frequency(second))

        Args:
            first_token: The first token in the pair.
            second_token: The second token in the pair.
            pair_freq: The frequency at which the pair occurs in the corpus.
            token_freqs: The dictionary containing token to frequency mappings.
        Returns:
            The WordPiece pair score, which is the pair's frequency normalized by the
            product of the individual token frequencies.
        """
        return pair_freq / (token_freqs[first_token] * token_freqs[second_token])

    @staticmethod
    def _compute_pair_scores(tokenized: list[str]) -> dict[tuple[str, str], float]:
        """
        Compute the WordPiece score for each consecutive pair of tokens in the corpus.

        Args:
            tokenized: The list of tokens.
        Returns:
            A dictionary, containing a mapping between consecutive token pairs and
            their scores.
        """
        token_freqs = defaultdict(int)
        pair_freqs = defaultdict(int)

        for tokens in tokenized:
            for token in tokens:
                token_freqs[token] += 1
            for pair in zip(tokens, tokens[1:]):
                pair_freqs[pair] += 1

        scores = {
            pair: WordPieceTokenizer._score_pair(*pair, freq, token_freqs)
            for pair, freq in pair_freqs.items()
        }
        return scores

    @staticmethod
    def _merge_tokens(
        pair: tuple[str, str], replacement: str, words: list[list[str]]
    ) -> dict[str, list[str]]:
        """
        Finds instances of the specified pair of consecutive tokens and replaces them
        with a new token.

        Args:
            pair: The pair of consecutive tokens to find and replace.
            replacement: The token with which to replace the pair of tokens.
            words: The words in which to replace the tokens.
        Returns:
            The list of words, with all instances of the target pair merged.

        Example:
            >>> WordPieceTokenizer._merge_tokens(
                ("a", "##b"),
                "ab",
                [["a", "##b", "##s"], ["a", "##r", "##c"], ["a", "##b", "##late"]]
            )
            [["ab", "##s"], ["a", "##r", "##c"], ["ab", "##late"]]
        """
        for tokens in words:
            i = 0
            while i < len(tokens) - 1:
                current = (tokens[i], tokens[i + 1])
                if current == pair:
                    tokens.pop(i + 1)
                    tokens[i] = replacement
                i += 1
        return words

    @staticmethod
    def _make_replacement(a: str, b: str) -> str:
        """
        Make a merged token from a pair of tokens.

        Args:
            a: The first token to merge.
            b: The second token to merge.
        Returns:
            The token created by merging.

        Example:
            >>> WordPieceTokenizer._make_replacement("h", "##i")
            "hi"
        """
        return a + (b[2:] if b.startswith("##") else b)

    @staticmethod
    def _get_character_tokens(word: str):
        """
        Split a word into its component character tokens, using the WordPiece style.
        This includes a "##" prefix before each non-leading character.

        Args:
            word: The word to split.
        Returns:
            A list of character tokens made from splitting the input.

        Examples:
            >>> WordTokenizer._get_character_tokens("banana")
            ["b", "##a", "##n", "##a", "##n", "##a"]
        """
        return [
            character if i == 0 else f"##{character}"
            for i, character in enumerate(word)
        ]

    def train(self, corpus: list[str]) -> None:
        """
        Trains a tokenizer using the WordPiece protocol. The training comprises the
        following steps:

        1. Pretokenizes the corpus, performing basic operations such as splitting on
        whitespace and punctuation.
        2. Converts each word in the corpus to character tokens. These character tokens
        make up the initial state of our vocabulary.
        3. Computes a score for each pair of consecutive tokens in the corpus, denoting
        how likely they are to occur next to each other.
        4. Selects the pair with the highest score to merge, replacing instances of the
        component tokens with the merged token and adding the merged token to the
        vocabulary.
        5. Repeats steps 3 and 4 until the desired vocabulary size is reached, or no
        more merges can be made (meaning each entire word in the corpus is in the
        vocabulary.)

        Args:
            corpus: The list of texts to use for training. Should contain a
            diverse set of words and punctuation marks.
        """
        pretokenized_words = [
            word for text in corpus for word in WordPieceTokenizer._pretokenize(text)
        ]

        word_tokens = [
            WordPieceTokenizer._get_character_tokens(word)
            for word in pretokenized_words
        ]

        self.vocab = list(set(token for word in word_tokens for token in word))
        self.vocab.extend(self.config.special_tokens)

        while len(self.vocab) < self.config.target_vocab_size:
            scores = self._compute_pair_scores(word_tokens)

            if not scores:
                warnings.warn(
                    "No more pairs left to merge, "
                    f"stopping training with {len(self.vocab)} tokens in vocabulary."
                )
                break

            merge_pair = max(scores, key=scores.get)
            replacement = self._make_replacement(*merge_pair)
            self.vocab.append(replacement)
            word_tokens = self._merge_tokens(merge_pair, replacement, word_tokens)

    @staticmethod
    def _make_all_prefix_substrings(string: str) -> list[str]:
        """
        Generates all prefix substrings from a given string.
        Utility function for `_encode_word`.

        Args:
            string: The string for which to generate the substrings.
        Returns:
            The list of all prefix substrings possible.

        Examples:
            >>> WordPieceTokenizer._make_all_prefix_substrings("garage")
            ["garage", "garag", "gara", "gar", "ga", "g", ""]
        """
        return [string[:-i] if i != 0 else string for i in range(len(string) + 1)]

    def _encode_word(self, word: str) -> list[str]:
        """
        Encodes a word using a longest-first matching strategy. Uses tokens from the
        vocabulary to encode the word.

        Args:
            word: The word to encode.
        Returns:
            The word encoded as tokens from the vocabulary.
        """
        vocab = self.vocab
        tokens = []

        while word:
            for substring in WordPieceTokenizer._make_all_prefix_substrings(word):
                if substring in vocab:
                    tokens.append(substring)
                    if len(substring) == len(word):
                        return tokens
                    else:
                        word = f"##{word[len(substring) :]}"
                        break
                elif not substring:
                    return [self.config.unknown_token]

    def tokenize(self, text: str) -> list[str]:
        """
        Tokenizes a text, converting it into a set of tokens contained in the
        tokenizer's vocabulary.

        Args:
            text: The text to tokenize.
        Returns:
            A list of tokens generated from encoding the input text.
        """
        pretokenized_words = WordPieceTokenizer._pretokenize(text)
        encoded = [
            token for word in pretokenized_words for token in self._encode_word(word)
        ]
        return [self.config.cls_token] + encoded

    def get_token_index(self, token: str) -> int:
        """
        Gets the index of a token in the tokenizer's vocabulary.

        Args:
            token: The token for which to find the index.
        Returns:
            The token's index in the vocabulary.
        """
        return self.vocab.index(token)

    def encode(
        self,
        text: str,
        padding: bool = False,
        padding_length: int | None = None,
    ) -> list[int]:
        """
        Encodes a text as a list of token IDs.

        Args:
            text: The text to encode.
            padding: `True` if output list should be padded to a certain length,
                     `False` otherwise.
            padding_length: The length to which the output lists should be padded.
        Returns:
            The token IDs of the tokenized text.
        """
        tokens = self.tokenize(text)
        token_ids = [self.get_token_index(token) for token in tokens]
        if padding:
            token_ids += [self.padding_token_id] * (padding_length - len(token_ids))
        return token_ids

    def batch_encode(
        self, texts: list[str], padding: bool = True, padding_length: int | None = None
    ) -> dict[str, torch.Tensor]:
        """
        Encodes a batch of texts as token ID lists.

        Args:
            texts: The list of texts to encode.
            padding: `True` if all the output token ID lists should be padded to a
                     certain length, `False` otherwise.
            padding_length: The length to which the output token ID lists should be
                            padded. If `None`, the output lists will be padded to the
                            length of the longest sequence in the batch.
        Returns:
            A dictionary with two entries: 'token_ids', containing the token IDs for
            each text sequence in the batch, and 'attention_mask', containing the
            attention masks for each sequence in the batch.
        """
        tokens = [self.tokenize(text) for text in texts]

        if padding_length is None:
            padding_length = max(len(t) for t in tokens)

        token_ids = [self.encode(text, padding, padding_length) for text in texts]

        attention_mask = [
            [0 if token_id == self.padding_token_id else 1 for token_id in toks]
            for toks in token_ids
        ]

        return {
            "token_ids": torch.tensor(token_ids),
            "attention_mask": torch.tensor(attention_mask),
        }

    def decode(
        self, token_ids: list[int], ignore_special_tokens: bool = True
    ) -> list[str]:
        """
        Decodes a text from a list of token IDs.

        Args:
            token_ids: The token IDs to decode.
            ignore_special_tokens: `True` if special tokens should be omitted from the
                                   output, `False` otherwise.
        Returns:
            The text decoded from the token IDs.
        """
        return [
            token
            for index in token_ids
            if (token := self.vocab[index]) not in self.config.special_tokens
            or not ignore_special_tokens
        ]

    def batch_decode(
        self, token_ids: list[list[int]], ignore_special_tokens: bool = True
    ) -> list[list[str]]:
        """
        Decodes texts from a batch of token IDs.

        Args:
            token_ids: The batch of token IDs to decode.
            ignore_special_tokens: `True` if special tokens should be omitted from the
                                   the output, `False` otherwise.
        Returns:
            The batch of texts decoded from the token IDs.
        """
        return [self.decode(tokens, ignore_special_tokens) for tokens in token_ids]

    @property
    def vocab_size(self) -> int:
        """The number of tokens in the vocabulary."""
        return len(self.vocab)

    @classmethod
    def from_pretrained(cls, name: str | Path) -> WordPieceTokenizer:
        """
        Load a pretrained tokenizer from a directory.

        Args:
            name: The name of the directory from which to load the model.
        Returns:
            A `WordPieceTokenizer` with a pretrained vocabulary and preset
            configuration.
        """
        name = resolve_checkpoint_path(name)

        with open(name / "tok_config.json", "r") as config_file:
            config_dict = json.load(config_file)
        config = TokenizerConfig(**config_dict)

        tokenizer = cls(config)

        with open(name / "vocab.txt", "r") as vocab_file:
            vocab = [line.strip() for line in vocab_file]

        tokenizer.vocab = vocab

        return tokenizer

    def save_pretrained(self, name: str | Path) -> None:
        """
        Save a pretrained tokenizer to a file.

        Args:
            directory: The directory to which to save the pretrained tokenizer.
        """
        name = Path(name)
        name.mkdir(parents=True, exist_ok=True)

        with open(name / "tok_config.json", "w") as config_file:
            json.dump(self.config.__dict__, config_file)

        with open(name / "vocab.txt", "w") as vocab_file:
            for token in self.vocab:
                vocab_file.write(f"{token}\n")

    @property
    def special_token_ids(self) -> list[int]:
        return [self.get_token_index(token) for token in self.config.special_tokens]

    @property
    def padding_token_id(self) -> int:
        return self.get_token_index(self.config.padding_token)

    @property
    def mask_token_id(self) -> int:
        return self.get_token_index(self.config.mask_token)
