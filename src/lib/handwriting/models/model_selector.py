import sys
import typing
import traceback
from .model_runner import _ProgressF, ModelRunner

from .vickianand.model_torch import ModelTorch
from .calligrapher.model_ulw import ModelULW
from .sjvasquez.model_tflite import ModelTFLite
from .sjvasquez.model_tf import ModelTF
from .sjvasquez.model_rnn import ModelRNN

def get_optimal_runner(progress_cb: _ProgressF) -> ModelRunner:
    return _load_model_from_list(progress_cb, ModelTorch, ModelULW, ModelTF, ModelRNN, ModelTFLite)

def _load_model_from_list(progress_cb: _ProgressF, *model_loaders: type[ModelRunner]) -> ModelRunner:
    for model_class in model_loaders:
        try:
            model = model_class(progress_cb)
            model.load_libraries()
            return model
        except Exception:
            print(f"Could not load \"{model_class.name}\" model runner ({model_class.__qualname__})")
            traceback.print_exc()
            print("---\n")

all_models = dict[str, type[ModelRunner]]()
all_models["Torch"] = ModelTorch
all_models["ULW"] = ModelULW
if False:
    all_models["TFLite"] = ModelTFLite
if not getattr(sys, "frozen", False):
    all_models["TF"] = ModelTF
if False:
    all_models["RNN"] = ModelRNN