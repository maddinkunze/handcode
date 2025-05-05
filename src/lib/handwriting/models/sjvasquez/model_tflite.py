import numpy as np
import tflite_runtime.interpreter as tflite # type: ignore
from .model_base import BaseTFModel, path_model_tflite

class ModelTFLite(BaseTFModel):
    name = "hws-tflite"

    def load(self):
        self._interpreter = tflite.Interpreter(path_model_tflite).get_signature_runner("classify")

    def invoke(self, text, biases, style):
        words_len, prime, prime_len, chars, chars_len, tsteps_max = self._prepare_inputs(text, style)

        return self._interpreter(
            prime=np.array([True]),
            x_prime=prime,
            x_prime_len=prime_len,
            num_samples=np.array([words_len]),
            sample_tsteps=np.array([tsteps_max]),
            chars=chars,
            chars_len=chars_len,
            bias=np.array(biases)
        )["strokes"]
