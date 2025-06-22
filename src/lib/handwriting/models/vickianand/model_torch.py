import os
import typing

if typing.TYPE_CHECKING:
    from lib.classproperty import classproperty
else:
    from classproperty import classproperty

from .alphabet import character_map
from ..model_runner import ModelRunner, WritingStyle

path_dir = os.path.abspath(os.path.dirname(__file__))
path_model = os.path.join(path_dir, "model.pt")
path_last_part = os.path.split(path_dir)[-1]

class ModelTorch(ModelRunner):
    id = "anand-torch"
    name = "Torch"
    alphabet = list(character_map.keys())
    writing_styles = [WritingStyle(0, "Default")]

    if typing.TYPE_CHECKING:
        import torch as _torch
        import numpy as _np
        from . import handwriting as _handwriting
    else:
        _torch_lib = None
        @classproperty
        def _torch(cls):
            if cls._torch_lib is None:
                import torch as _torch_lib
                cls._torch_lib = _torch_lib
            return cls._torch_lib

        _np_lib = None
        @classproperty
        def _np(cls):
            if cls._np_lib is None:
                import numpy as _np_lib
                cls._np_lib = _np_lib
            return cls._np_lib
        
        _handwriting_lib = None
        @classproperty
        def _handwriting(cls):
            if cls._handwriting_lib is None:
                from . import handwriting as _handwriting_lib
                cls._handwriting_lib = _handwriting_lib
            return cls._handwriting_lib
        
    _device_int = None
    @classproperty
    def _device(cls):
        if cls._device_int is None:
            cls._device_int = cls._torch.device("cpu") # TODO: maybe check if cuda is available?
        return cls._device_int
    
    _model_int = None
    @classproperty
    def _model(cls):
        if cls._model_int is None:
            cls._model_int = cls._handwriting.HandWritingSynthRNN()
            cls._model_int.load_state_dict(cls._torch.load(path_model, map_location=cls._device))
        return cls._model_int
    
    _ohenc_int = None
    @classproperty
    def _oh_encoder(cls):
        if cls._ohenc_int is None:
            cls._ohenc_int = cls._handwriting.OneHotEncoder()
        return cls._ohenc_int

    def load_libraries(self):
        super().load_libraries()
        self._np
        self._torch
        self._handwriting

    def load(self):
        self._device
        self._model
        self._oh_encoder

    def invoke(self, text, biases, style):
        biases = [3 * b for b in biases]
        text = [e.to(self._device) for e in self._oh_encoder.one_hot(text)]
        strokes = self._model.generate(text, biases[0], self._device, True).cpu().numpy()
        strokes_words = []
        for i in range(strokes.shape[1]):
            strokes_word = strokes[:, i, :]
            
            penup_indices = self._np.argwhere(strokes_word[:, 0] == 1.0)
            if not penup_indices.size > 0:
                continue # TODO: throw an error??

            last_actual_index = penup_indices[-1, 0] # find where garbage at the end starts
            strokes_word = strokes_word[:, :last_actual_index] # cut garbage from the end
            strokes_word[:, :] = strokes_word[:, (1, 2, 0)] # reorder the entries (the model returns (penup, x, y), but we need (x, y, penup))
            strokes_words.append(strokes_word)
        return strokes_words
    
    urls = [
        ("Base Model", "https://github.com/vickianand/handwriting-synthesis"),
        ("Source Code", ModelRunner._base_url + path_last_part),
    ]
    _license = None
    _description = None
    _short_info = None
    @classmethod
    def _load_info(cls):
        cls._description, cls._license, cls._short_info = cls._get_info_from_readme(os.path.join(path_dir, "README.md"), os.path.join(path_dir, "LICENSE"))
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
    @classproperty
    def short_info(cls):
        if cls._short_info is None:
            cls._load_info()
        return cls._short_info
    
    @classmethod
    def is_available(cls) -> bool:
        return True