import tensorflow as tf
from .model_base import BaseTFModel, path_model_tflite

class ModelTF(BaseTFModel):
    name = "hws-tf"

    def load(self):
        self._interpreter = tf.lite.Interpreter(path_model_tflite).get_signature_runner("classify")

    def invoke(self, text, biases, style):
        words_len, prime, prime_len, chars, chars_len, tsteps_max = self._prepare_inputs(text, style)

        return self._interpreter(
            prime = tf.constant(True),
            x_prime = tf.constant(prime.astype("float32")),
            x_prime_len = tf.constant(prime_len.astype("int32")),
            num_samples = tf.constant(words_len),
            sample_tsteps = tf.constant(tsteps_max),
            chars = tf.constant(chars.astype("int32")),
            chars_len = tf.constant(chars_len.astype("int32")),
            bias = tf.constant(biases)
        )["strokes"]
