import os
import torch
import numpy as np

from .alphabet import character_map
from .handwriting import HandWritingSynthRNN, OneHotEncoder
from ..model_runner import ModelRunner, WritingStyle

path_dir = os.path.abspath(os.path.dirname(__file__))
path_model = os.path.join(path_dir, "model.pt")

class ModelTorch(ModelRunner):
    name = "anand-torch"
    alphabet = list(character_map.keys())
    writing_styles = [WritingStyle(0, "Default")]

    def load(self):
        self._device = torch.device("cpu")
        self._model = HandWritingSynthRNN()
        self._model.load_state_dict(torch.load(path_model, map_location=self._device))
        self._oh_encoder = OneHotEncoder()

    def invoke(self, text, biases, style):
        text = [e.to(self._device) for e in self._oh_encoder.one_hot(text)]
        strokes = self._model.generate(text, biases[0], self._device, True).cpu().numpy()
        strokes_words = []
        for i in range(strokes.shape[1]):
            strokes_word = strokes[:, i, :]
            last_actual_index = np.argwhere(strokes_word[:, 0] == 1.0)[-1, 0] # find where garbage at the end starts
            strokes_word = strokes_word[:, :last_actual_index] # cut garbage from the end
            strokes_word[:, :] = strokes_word[:, (1, 2, 0)] # reorder the entries (the model returns (penup, x, y), but we need (x, y, penup))
            strokes_words.append(strokes_word)
        return strokes_words