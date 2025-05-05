import os
import typing
import numpy as np

from .alphabet import character_map
from ..model_runner import ModelRunner, WritingStyle

path_dir = os.path.abspath(os.path.dirname(__file__))
path_styles = os.path.join(path_dir, "styles")
path_checkpoints = os.path.join(path_dir, "checkpoints")
path_model_tflite = os.path.join(path_dir, "model.tflite")

class BaseTFModel(ModelRunner):
    alphabet = list[character_map.keys()]
    writing_styles = [WritingStyle(i, f"Style {i+1}") for i in range(13)]

    class _StyleEntry(typing.TypedDict):
        strokes: np.ndarray
        chars: np.ndarray
    _cached_styles = dict[int, _StyleEntry]()
    @classmethod
    def _load_style(cls, style: int):
        cached_style = cls._cached_styles.get(style, None)
        if cached_style:
            return cached_style

        strokes = np.load(os.path.join(path_styles, f"style-{style}-strokes.npy"))
        chars = np.load(os.path.join(path_styles, f"style-{style}-chars.npy"))

        cached_style = {"strokes": strokes, "chars": chars}
        cls._cached_styles[style] = cached_style
        return cached_style

    @staticmethod
    def _encode_ascii(text):
        return np.array(list(map(lambda x: character_map.get(x, 0), text)) + [0])

    @classmethod
    def _prepare_inputs(cls, text, style):
        words_len = len(text)

        prime = np.zeros([words_len, 1200, 3])
        prime_len = np.zeros([words_len])

        chars = np.zeros([words_len, 120])
        chars_len = np.zeros([words_len])

        tsteps_max = max(map(len, text))

        style = cls._load_style(style)
        style_chars = style["chars"]
        style_strokes = style["strokes"]
        style_strokes_len = len(style_strokes)

        for i, word in enumerate(text):
            _chars = f"{style_chars} {word}"
            _chars = cls._encode_ascii(_chars)
            _chars = np.array(_chars)
            _chars_len = len(_chars)

            prime[i, :style_strokes_len, :] = style_strokes
            prime_len[i] = style_strokes_len

            chars[i, :_chars_len] = _chars
            chars_len[i] = _chars_len

        return words_len, prime, prime_len, chars, chars_len, tsteps_max
