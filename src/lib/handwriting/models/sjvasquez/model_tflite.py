import typing
if typing.TYPE_CHECKING:
    from lib.classproperty import classproperty
else:
    from classproperty import classproperty
from .model_base import BaseTFModel, path_model_tflite

class ModelTFLite(BaseTFModel):
    id = "hws-tflite"
    name = "TFLite"

    if typing.TYPE_CHECKING:
        import tflite_runtime.interpreter as _tflite
    else:
        _tflite_lib = None
        @classproperty
        def _tflite(cls):
            if cls._tflite_lib is None:
                import tflite_runtime.interpreter as _tflite_lib
                cls._tflite_lib = _tflite_lib
            return cls._tflite_lib

    _interpreter_int = None
    @classproperty
    def _interpreter(cls):
        if cls._interpreter_int is None:
            cls._interpreter_int = cls._tflite.Interpreter(path_model_tflite).get_signature_runner("classify")
        return cls._interpreter_int

    def load_libraries(self):
        super().load_libraries()
        self._tflite

    def load(self):
        self._interpreter

    def invoke(self, text, biases, style):
        words_len, prime, prime_len, chars, chars_len, tsteps_max = self._prepare_inputs(text, style)

        return self._interpreter(
            prime=self._np.array([True]),
            x_prime=prime,
            x_prime_len=prime_len,
            num_samples=self._np.array([words_len]),
            sample_tsteps=self._np.array([tsteps_max]),
            chars=chars,
            chars_len=chars_len,
            bias=self._np.array(biases)
        )["strokes"]

    @classmethod
    def is_available(cls):
        # there is basically no tflite runtime (except for android), that includes flex delegates (which are required for this model), so we always disable it by default
        return False