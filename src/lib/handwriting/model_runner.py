import os
import sys
import typing
import numpy as np
import traceback

_T = typing.TypeVar("_T")
_ProgressF = typing.Callable[[str, float|int, float|int], typing.Any]
_InvokeF = typing.Callable[[_T, bool, np.ndarray, np.ndarray, int, int, np.ndarray, np.ndarray, list[float], int, _ProgressF], list[list[float]]]

class WritingStyle:
    def __init__(self, sid: int, name: str, image_path: str|None=None):
        self.id = sid
        self.name = name
        self.image_path = image_path

class ModelRunner(typing.Generic[_T]):
    def __init__(self, load_f: typing.Callable[[], _T], invoke_f: _InvokeF, model_name: str, writing_styles: list[WritingStyle], prepend_style_chars: bool=True):
        self._model = None
        self.load_f = load_f
        self.invoke_f = invoke_f
        self.model_name = model_name
        self.writing_styles = writing_styles
        self.prepend_style_chars = prepend_style_chars

    def load(self):
        self._model = self.load_f()

    def invoke(self, prime: bool, x_prime: np.ndarray, prime_len: np.ndarray, num_samples: int, sample_tsteps: int, chars: np.ndarray, chars_len: np.ndarray, biases: list[float], style_index: int, progress_cb: _ProgressF) -> list[list[float]]:
        return self.invoke_f(self._model, prime, x_prime, prime_len, num_samples, sample_tsteps, chars, chars_len, biases, style_index, progress_cb)

path_dir = os.path.dirname(os.path.abspath(__file__))
path_model_ulw = os.path.join(path_dir, "model.ulw")
path_model_tflite = os.path.join(path_dir, "model.tflite")

def get_optimal_runner() -> ModelRunner:
    """
    Get optimal ModelRunner for this platform/execution environment
    """

    try:
        return get_ultralightweight_runner()
    except:
        print("Could not load ultralightweight model runner:")
        traceback.print_exc()
        print("---\n")

    if sys.platform.lower() in []: # ["linux", "linux2", "macos"]: # tflite runtime is disabled, because no platform seems to include the flex operators by default in the tflite_runtime
        try:
            return get_tflite_runner()
        except: 
            print("Could not load tflite runner:")
            traceback.print_exc()
            print("---\n")

    try:
        return get_tensorflow_runner()
    except:
        print("Could not load tensorflow runner:")
        traceback.print_exc()
        print("---\n")

    try:
        return get_checkpoint_runner() # this will only work in very old versions of tensorflow (like <= 1.15 i think)
    except:
        print("Could not load checkpoint runner:")
        traceback.print_exc()
        print("---\n")

    raise NotImplementedError("Could not load a model runner on this system. Please check the stdout (terminal) for more information.")

ulw_writing_styles = [WritingStyle(i, f"Style {i}") for i in range(1, 10)]

def get_ultralightweight_runner() -> ModelRunner:
    """
    Creates a model runner using an ultra-lightweight model, that depends on numpy only
    """
    from .model_ulw import parse_model as load_ulw_model, run_model as run_ulw_model

    def load_model():
        return load_ulw_model(path_model_ulw)
    
    def invoke_model(model, prime: bool, x_prime: np.ndarray, prime_len: np.ndarray, num_samples: int, sample_tsteps: int, chars: np.ndarray, chars_len: np.ndarray, biases: list[float], style_index: int, progress_cb: _ProgressF) -> list[list[float]]:
        strokes = run_ulw_model(
            model,
            chars,
            style_index,
            biases,
            sample_tsteps,
            progress_cb,
        )
        return filter_strokes(strokes)
    
    return ModelRunner(load_model, invoke_model, "ulw", ulw_writing_styles, prepend_style_chars=False)

original_writing_styles = [WritingStyle(i, f"Style {i+1}") for i in range(13)]

def get_tflite_runner() -> ModelRunner:
    """
    Creates a model runner using only the tflite runtime, only works an machines, where the flex delegate was compiled into tflite
    """
    import tflite_runtime.interpreter as tflite # type: ignore
    import numpy as np
    
    def load_model():
        return tflite.Interpreter(path_model_tflite).get_signature_runner("classify")

    def invoke_model(interpreter, prime: bool, x_prime: np.ndarray, prime_len: np.ndarray, num_samples: int, sample_tsteps: int, chars: np.ndarray, chars_len: np.ndarray, biases: list[float], style_index: int, progress_cb: _ProgressF) -> list[list[float]]:
        strokes = interpreter(
            prime=np.array([prime]),
            x_prime=x_prime,
            x_prime_len=prime_len,
            num_samples=np.array([num_samples]),
            sample_tsteps=np.array([sample_tsteps]),
            chars=chars,
            chars_len=chars_len,
            bias=np.array(biases)
        )["strokes"]
        return filter_strokes(strokes)

    return ModelRunner(load_model, invoke_model, "tflite", original_writing_styles)
    
def get_tensorflow_runner() -> ModelRunner:
    import tensorflow as tf # type: ignore

    def load_model():
        return tf.lite.Interpreter(path_model_tflite).get_signature_runner("classify")

    def invoke_model(interpreter, prime: bool, x_prime: np.ndarray, prime_len: np.ndarray, num_samples: int, sample_tsteps: int, chars: np.ndarray, chars_len: np.ndarray, biases: list[float], style_index: int, progress_cb: _ProgressF) -> list[list[float]]:
        strokes = interpreter(
            prime = tf.constant(prime),
            x_prime = tf.constant(x_prime.astype("float32")),
            x_prime_len = tf.constant(prime_len.astype("int32")),
            num_samples = tf.constant(num_samples),
            sample_tsteps = tf.constant(sample_tsteps),
            chars = tf.constant(chars.astype("int32")),
            chars_len = tf.constant(chars_len.astype("int32")),
            bias = tf.constant(biases)
        )["strokes"]
        return filter_strokes(strokes)

    return ModelRunner(load_model, invoke_model, "tensorflow", original_writing_styles)
    
def get_checkpoint_runner() -> ModelRunner:
    from .rnn import rnn
    import tensorflow as tf # type: ignore
    
    def load_model():
        model = rnn(
            log_dir=os.path.join(path_dir, 'logs'),
            checkpoint_dir=os.path.join(path_dir, 'checkpoints'),
            prediction_dir=os.path.join(path_dir, 'predictions'),
            learning_rates=[.0001, .00005, .00002],
            batch_sizes=[32, 64, 64],
            patiences=[1500, 1000, 500],
            beta1_decays=[.9, .9, .9],
            validation_batch_size=32,
            optimizer='rms',
            num_training_steps=100000,
            warm_start_init_step=17900,
            regularization_constant=0.0,
            keep_prob=1.0,
            enable_parameter_averaging=False,
            min_steps_to_checkpoint=2000,
            log_interval=20,
            grad_clip=10,
            lstm_size=400,
            output_mixture_components=20,
            attention_mixture_components=10
        )
        model.restore()
        return model

    def invoke_model(interpreter, prime: bool, x_prime: np.ndarray, prime_len: np.ndarray, num_samples: int, sample_tsteps: int, chars: np.ndarray, chars_len: np.ndarray, biases: list[float], style_index: int, progress_cb: _ProgressF) -> list[list[float]]:
        strokes = interpreter.session.run(
            [interpreter.sampled_sequence],
            feed_dict = {
                interpreter.prime: prime,
                interpreter.x_prime: x_prime,
                interpreter.x_prime_len: prime_len,
                interpreter.num_samples: num_samples,
                interpreter.sample_tsteps: sample_tsteps,
                interpreter.c: chars,
                interpreter.c_len: chars_len,
                interpreter.bias: biases
            }
        )[0].numpy()
        return filter_strokes(strokes)

    return ModelRunner(load_model, invoke_model, "checkpoint", original_writing_styles)

def filter_strokes(strokes) -> list[list[float]]:
    return [stroke[~np.all(stroke == 0.0, axis=1)] for stroke in strokes]