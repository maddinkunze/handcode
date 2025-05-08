import typing
import traceback
from .model_runner import _ProgressF, ModelRunner

def get_optimal_runner(progress_cb: _ProgressF) -> ModelRunner:
    return _load_model_from_list(progress_cb, get_torch_model, get_ulw_model, get_tf_model, get_rnn_model)

def _load_model_from_list(progress_cb: _ProgressF, *model_loaders: typing.Callable[[], type[ModelRunner]]) -> ModelRunner:
    for loader in model_loaders:
        loader_name = loader.__qualname__
        try:
            model_class = loader()
            loader_name = f"{loader_name} -> {model_class.name} ({model_class.__qualname__})"
            return model_class(progress_cb)
        except Exception:
            print(f"Could not load \"{loader_name}\" model runner")
            traceback.print_exc()
            print("---\n")

def get_torch_model() -> type[ModelRunner]:
    from .vickianand.model_torch import ModelTorch
    return ModelTorch

def get_ulw_model() -> type[ModelRunner]:
    from .calligrapher.model_ulw import ModelULW
    return ModelULW

def get_tflite_model() -> type[ModelRunner]:
    from .sjvasquez.model_tflite import ModelTFLite
    return ModelTFLite

def get_tf_model() -> type[ModelRunner]:
    from .sjvasquez.model_tf import ModelTF
    return ModelTF

def get_rnn_model() -> type[ModelRunner]:
    from .sjvasquez.model_rnn import ModelRNN
    return ModelRNN
