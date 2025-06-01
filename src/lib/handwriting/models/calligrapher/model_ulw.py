import os
import typing
if typing.TYPE_CHECKING:
    from lib.classproperty import classproperty
else:
    from classproperty import classproperty
from ..model_runner import ModelRunner, WritingStyle

path_dir = os.path.abspath(os.path.dirname(__file__))
path_model = os.path.join(path_dir, "model.ulw")
path_last_part = os.path.split(path_dir)[-1]

class ModelULW(ModelRunner):
    id = "cai-ulw"
    name = "ULW"
    writing_styles = [WritingStyle(i, f"Style {i}") for i in range(1, 10)]

    if typing.TYPE_CHECKING:
        from . import rnn as _rnn
    else:
        _rnn_lib = None
        @classproperty
        def _rnn(cls):
            if cls._rnn_lib is None:
                from . import rnn as _rnn_lib
                cls._rnn_lib = _rnn_lib
            return cls._rnn_lib

    _model_int = None
    @classproperty
    def _model(cls):
        if cls._model_int is None:
            cls._model_int = cls._rnn.parse_model(path_model)
        return cls._model_int

    def load_libraries(self):
        super().load_libraries()
        self._rnn

    def load(self):
        self._model

    def invoke(self, text, biases, style):
        biases = [2.5 * b for b in biases]
        return self._rnn.run_model(self._model, text, style.id, biases, self.progress_cb)
    
    urls = [
        ("Web Demo", "https://caligrapher.ai/"),
        ("Base Model", "https://github.com/sjvasquez/handwriting-synthesis"),
        ("Source Code", ModelRunner._base_url + path_last_part),
    ]
    _license = None
    _description = None
    _short_info = None
    @classmethod
    def _load_info(cls):
        cls._description, cls._license, cls._short_info = cls._get_info_from_readme(os.path.join(path_dir, "README.md"))
        related = "sjvasquez"
        _, license, _ = cls._get_info_from_readme(os.path.join(path_dir, os.path.pardir, related, "README.md"))
        if license:
            cls._license += f"\n\nLicense information of the related project ({related}):\n{license}"
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
    def is_available(cls):
        return True
