import os
import typing
if typing.TYPE_CHECKING:
    from lib.classproperty import classproperty
else:
    from classproperty import classproperty

from .alphabet import character_map
from ..model_runner import ModelRunner, WritingStyle

path_dir = os.path.abspath(os.path.dirname(__file__))
path_styles = os.path.join(path_dir, "styles")
path_checkpoints = os.path.join(path_dir, "checkpoints")
path_model_tflite = os.path.join(path_dir, "model.tflite")
path_last_part = os.path.split(path_dir)[-1]

class BaseTFModel(ModelRunner):
    alphabet = list[character_map.keys()]
    writing_styles = [WritingStyle(i, f"Style {i+1}") for i in range(13)]

    if typing.TYPE_CHECKING:
        import numpy as _np
    else:
        _np_lib = None
        @classproperty
        def _np(cls):
            if cls._np_lib is None:
                import numpy as _np_lib
                cls._np_lib = _np_lib
            return cls._np_lib

    class _StyleEntry(typing.TypedDict):
        strokes: "BaseTFModel._np.ndarray"
        chars: "BaseTFModel._np.ndarray"
    _cached_styles = dict[int, _StyleEntry]()
    @classmethod
    def _load_style(cls, style: int):
        cached_style = cls._cached_styles.get(style, None)
        if cached_style:
            return cached_style

        strokes = cls._np.load(os.path.join(path_styles, f"style-{style}-strokes.npy"))
        chars = cls._np.load(os.path.join(path_styles, f"style-{style}-chars.npy"))

        cached_style = {"strokes": strokes, "chars": chars}
        cls._cached_styles[style] = cached_style
        return cached_style

    @staticmethod
    def _encode_ascii(text):
        import numpy as np
        return np.array(list(map(lambda x: character_map.get(x, 0), text)) + [0])

    @classmethod
    def _prepare_inputs(cls, text, style):
        words_len = len(text)

        prime = cls._np.zeros([words_len, 1200, 3])
        prime_len = cls._np.zeros([words_len])

        chars = cls._np.zeros([words_len, 120])
        chars_len = cls._np.zeros([words_len])

        tsteps_max = max(map(len, text))

        style = cls._load_style(style)
        style_chars = style["chars"]
        style_strokes = style["strokes"]
        style_strokes_len = len(style_strokes)

        for i, word in enumerate(text):
            _chars = f"{style_chars} {word}"
            _chars = cls._encode_ascii(_chars)
            _chars = cls._np.array(_chars)
            _chars_len = len(_chars)

            prime[i, :style_strokes_len, :] = style_strokes
            prime_len[i] = style_strokes_len

            chars[i, :_chars_len] = _chars
            chars_len[i] = _chars_len

        return words_len, prime, prime_len, chars, chars_len, tsteps_max

    def load_libraries(self):
        super().load_libraries()
        self._np

    urls = [
        ("Base Model", "https://github.com/sjvasquez/handwriting-synthesis"),
        ("Source Code", ModelRunner._base_url + path_last_part),
    ]
    _license = None
    _description = None
    short_info = "❌ Commercial use prohibited\n⚖️ Unknown License"
    @classmethod
    def _load_info(cls):
        cls._description, cls._license, _ = cls._get_info_from_readme(os.path.join(path_dir, "README.md"))
    @classproperty
    def license(cls):
        if cls._license is None:
            cls._load_info()
        return cls._license
    @classproperty
    def description(cls):
        if cls._description is None:
            cls._load_info()
        return cls._description