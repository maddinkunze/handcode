import typing
if typing.TYPE_CHECKING:
    from lib.classproperty import classproperty
else:
    from classproperty import classproperty

from .model_base import BaseTFModel, path_model_tflite

class ModelTF(BaseTFModel):
    name = "hws-tf"


    if typing.TYPE_CHECKING:
        import tensorflow as _tf
    else:
        _tf_lib = None
        @classproperty
        def _tf(cls):
            if cls._tf_lib is None:
                import tensorflow as _tf_lib
                cls._tf_lib = _tf_lib
            return cls._tf_lib

    _interpreter_int = None
    @classproperty
    def _interpreter(cls):
        if cls._interpreter_int is None:
            cls._interpreter_int = cls._tf.lite.Interpreter(path_model_tflite).get_signature_runner("classify")
        return cls._interpreter_int

    def load_libraries(self):
        super().load_libraries()
        self._tf

    def load(self):
        self._interpreter

    def invoke(self, text, biases, style):
        words_len, prime, prime_len, chars, chars_len, tsteps_max = self._prepare_inputs(text, style)

        return self._interpreter(
            prime = self._tf.constant(True),
            x_prime = self._tf.constant(prime.astype("float32")),
            x_prime_len = self._tf.constant(prime_len.astype("int32")),
            num_samples = self._tf.constant(words_len),
            sample_tsteps = self._tf.constant(tsteps_max),
            chars = self._tf.constant(chars.astype("int32")),
            chars_len = self._tf.constant(chars_len.astype("int32")),
            bias = self._tf.constant(biases)
        )["strokes"]
