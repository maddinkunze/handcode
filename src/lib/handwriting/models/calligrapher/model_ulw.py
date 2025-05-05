import os
import math
import numpy as np
import typing
import random

from ..model_runner import ModelRunner, WritingStyle

def load_model(filepath: str) -> bytes:
    f = open(filepath, "rb")
    content = f.read()
    f.close()
    return content

def parse_model(filepath: str):
    model_raw = load_model(filepath)
    model_raw_length = len(model_raw)

    model_parsed = {}
    index = 0

    while index < model_raw_length:
        name_length = model_raw[index]
        index += 1

        name = model_raw[index:index+name_length].decode()
        index += name_length

        has_extra_data = model_raw[index]
        index += 1

        chunk_length = int.from_bytes(model_raw[index:index+4], byteorder="little")
        index += 4

        chunk_length_bytes = chunk_length * 4
        chunk = bytes_to_float32(model_raw[index:index+chunk_length_bytes])
        index += chunk_length_bytes

        offsets = None
        if has_extra_data:
            offsets_length_bytes = chunk_length * 1
            offsets = bytes_to_uint8(model_raw[index:index+offsets_length_bytes])
            index += offsets_length_bytes

        dimensions_length = model_raw[index]
        index += 1

        dimensions_length_bytes = dimensions_length * 2
        matrix_dimensions = bytes_to_uint16(model_raw[index:index+dimensions_length_bytes])
        index += dimensions_length_bytes

        if name in ["y", "w", "r", "l"]:
            chunk = process_model_weights(chunk, offsets, matrix_dimensions)
        elif has_extra_data:
            chunk = unpack_sparse_matrix(chunk, offsets, matrix_dimensions)

        model_parsed[name] = chunk

    return model_parsed

def bytes_to_float32(data: bytes) -> np.ndarray:
    """Convert bytes to float32."""
    return np.frombuffer(data, dtype=np.float32).newbyteorder("<")  # data comes in little endian

def bytes_to_uint8(data: bytes) -> np.ndarray:
    """Convert bytes to uint8."""
    return np.frombuffer(data, dtype=np.uint8).newbyteorder("<")  # data comes in little endian

def bytes_to_uint16(data: bytes) -> np.ndarray:
    """Convert bytes to uint16."""
    return np.frombuffer(data, dtype=np.uint16).newbyteorder("<")  # data comes in little endian

def process_model_weights(weights, cumulative_offsets, matrix_dimensions):
    cumulative_sum = 0
    non_zero_weights = []
    column_offsets = []
    row_indices = []

    for idx in range(len(weights)):
        weight = weights[idx]
        cumulative_sum += cumulative_offsets[idx]
        row_index = math.floor(cumulative_sum / matrix_dimensions[1])
        column_offset = cumulative_sum % matrix_dimensions[1]
        if weight != 0:
            non_zero_weights.append(weight)
            column_offsets.append(column_offset)
            row_indices.append(row_index)

    row_start_indices = [0]
    current_index = 0
    row_indices_length = len(row_indices)
    for row in range(matrix_dimensions[0]):
        while (current_index < row_indices_length) and (row_indices[current_index] == row):
            current_index += 1
        row_start_indices.append(current_index)

    return [np.array(matrix_dimensions), np.array(non_zero_weights), np.array(column_offsets), np.array(row_start_indices)]

def unpack_sparse_matrix(values, offsets, dimensions):
    total_elements = np.prod(dimensions)
    sparse_matrix = np.zeros(total_elements, dtype=np.float32)
    num_values = len(values)
    cumulative_offset = 0

    for i in range(num_values):
        value = values[i]
        cumulative_offset += offsets[i]
        sparse_matrix[cumulative_offset] = value

    return sparse_matrix


character_map = {
    "\0": 0, " ": 8,  "!": 72, '"': 4,  "#": 56, "'": 16, "(": 66, ")": 67, ",": 37, "-": 40, ".": 7,  "?": 51,
    "0": 62, "1": 59, "2": 63, "3": 69, "4": 68, "5": 61, "6": 71, "7": 70, "8": 76, "9": 60, ":": 74, ";": 73,
    "A": 9,  "B": 47, "C": 57, "D": 52, "E": 42, "F": 53, "G": 45, "H": 41, "I": 23, "J": 64, "K": 58, "L": 48,
    "M": 5,  "N": 38, "O": 36, "P": 46, "R": 55, "S": 18, "T": 31, "U": 65, "V": 39, "W": 54, "Y": 50,
    "a": 14, "b": 32, "c": 20, "d": 27, "e": 19, "f": 35, "g": 33, "h": 30, "i": 13, "j": 43, "k": 28, "l": 26,
    "m": 12, "n": 15, "o": 25, "p": 29, "q": 49, "r": 6,  "s": 17, "t": 21, "u": 11, "v": 34, "w": 24, "x": 44,
    "y": 22, "z": 10,
}

writing_style_map = {
    1:  44,
    2:  54,
    3:  23,
    4:  1,
    5:  19,
    6:  6,
    7:  30,
    8:  11,
    9:  21,
}

def run_model(model: dict, text: list[str], writing_style: int, biases: list[float], progress_cb: typing.Callable[[str|None, float|int, float|int], typing.Any]):
    num_words = len(text)
    progress_cb(None, 0, num_words)

    writing_style_index = writing_style_map[writing_style]

    strokes_all = []

    for i, (word, bias) in enumerate(zip(text, biases)):
        word_stripped = np.trim_zeros(word)
        word_filtered = [character_map.get(c, 0) for c in word_stripped]
        word_filtered = [c for c in word_filtered if c != 0]
        word_filtered = [2, *word_filtered, 3]
        word_len = len(word_filtered)

        er = calculate_char_embeddings(model, word_filtered)

        writing_styles = model["g"].reshape(-1, 64)
        o = writing_styles[writing_style_index]
        n = model["k"].reshape(64, -1).T
        v = model["R"]
        o = np.sum(o * n, axis=1) + v

        state = [
            model["d"],
            model["o"],
            model["e"],
            model["m"],
            model["x"],
            model["a"],
            model["T"],
            np.zeros(10, dtype=np.float32),
            np.zeros((10, word_len+1)) + np.arange(word_len+1) - 0.5,
            o,
            er,
        ]

        sample_tsteps = 0
        strokes = [np.array([0, 0, 1])]

        stop_condition = 40 * len(word)

        while True:
            stroke, stop_certainty, state = js_L(model, strokes[-1], state, bias)
            sample_tsteps += 1
            if (sample_tsteps > stop_condition) or (stop_certainty > .5):
                break
            progress_cb(None, i + sample_tsteps / stop_condition, num_words)
            strokes.append(stroke)

        strokes_all.append(np.array(strokes))

    return strokes_all

def js_L(model, r, state, bias):
    t, stop_certainty = js_F(model, r, state)
    return [js_U(t, bias), stop_certainty, state]

def js_F(model, r, state):
    t = np.sum(r.reshape(-1, 1) * model["i"].reshape(-1, 256), axis=0)
    t += model["W"] * state[9] # 9 = e.z
    t = t * math.sqrt(1 / 2)
    a = rnn_layer(model, t, state, 1)
    t = (t + a) * math.sqrt(1 / 2)
    l = np.concatenate((t, state[6])) # 6 = e.w
    n = rnn_layer(model, l, state, 2)
    i = js_k(model, n, state)
    f = np.concatenate((n, i))
    f = compute_weighted_group_sums(f, model["l"])
    f = f + model["Q"]
    f = np.tanh(f)
    t = (t + f) * math.sqrt(1 / 2)
    stop_probability = sigmoid(np.sum(i * model["c"]) + model["u"])
    d = rnn_layer(model, t, state, 3)
    t = (t + d) * math.sqrt(1 / 2)
    c = np.sum(t.reshape(-1, 1) * model["z"].reshape(256, -1), axis=0)
    c = c + model["v"]
    return c, stop_probability

def js_k(model, r, state):
    t = np.sum(r.reshape(-1, 1) * model["h"].reshape(256, -1), axis=0)
    t = t + model["n"]
    a, l, v = np.split(t, 3)
    l = softplus(l)
    v = softplus(v)
    a = softmax(a)
    v = state[7] + (v / 15) # 7 = e.k
    state[7] = v
    i = state[8] # 8 = e.u
    a = a.reshape(10, -1)
    l = l.reshape(10, -1)
    v = v.reshape(10, -1)
    c = sigmoid((i - v) / l)

    p = a * np.diff(c)

    w = p.sum(axis=0)
    t = state[10]
    g = np.sum(w.reshape(-1, 1) * t, axis=0)
    state[6] = g # 6 = e.w
    return g

def softmax(r):
    e = np.exp(r)
    return e / np.sum(e)

def rnn_layer(model, r, state, stage):
    if stage == 1:
        a = state[0] # 0 = e.a
        l = state[3] # 3 = e.d
        n = model["y"]
        i = model["p"]
    elif stage == 2:
        a = state[1] # 1 = e.b
        l = state[4] # 4 = e.e
        n = model["w"]
        i = model["q"]
    else:
        a = state[2] # 2 = e.c
        l = state[5] # 5 = e.f
        n = model["r"]
        i = model["f"]

    r = np.concatenate((r, l))
    f = compute_weighted_group_sums(r, n) + i
    h, d, c, p = np.split(f, 4)
    m = sigmoid(c) * a + sigmoid(h) * np.tanh(d)
    M = sigmoid(p) * np.tanh(m)

    if stage == 1:
        state[0] = m # 0 = e.a
        state[3] = M # 3 = e.d
    elif stage == 2:
        state[1] = m # 1 = e.b
        state[4] = M # 4 = e.e
    else:
        state[2] = m # 2 = e.c
        state[5] = M # 5 = e.f
    return M

def compute_weighted_group_sums(r, e):
    matrix_shape, weights, column_offsets, start_indices = e
    weights_premultiplied = weights * r[column_offsets]
    return np.array([np.sum(weights_premultiplied[start:end]) for start, end in zip(start_indices[:-1], start_indices[1:])])

def js_U(r, bias):
    e = r[:120]
    a = sigmoid(r[120:])[0]
    penup = 1 if random.random() < a else 0
    
    e = e.reshape(-1, 6)
    f = e[:, 0]
    c = e[:, 1:3].flatten()
    p = e[:, 3]
    w = e[:, 4:6].flatten()

    p = np.tanh(p)
    g = bias
    c = softplus(c) / np.exp(g)
    f = np.log(softmax(f)) * (1 + g)

    for i in range(len(f)):
        if f[i] < np.log(0.02):
            f[i] -= 100

    b = np.argmax(f - np.log(-np.log(np.random.random(f.shape))))
    M = extract_elements_by_indices(w, b, 2)
    y = extract_elements_by_indices(c, b, 2)
    C = extract_elements_by_indices(p, b, 1)[0]
    A = y[0]
    k = y[1]
    F = np.array([[A, 0], [C * k, k * np.sqrt(1 - C * C)]])

    U = np.sqrt(-2 * np.log(1 - np.random.random(2))) * np.cos(2 * np.pi * np.random.random(2))
    L = M + np.sum(U * F, axis=1)
    return np.array([L[0], L[1], penup])

def extract_elements_by_indices(array, indices, group_size):
    return array.reshape(-1, group_size)[indices].flatten()

def calculate_char_embeddings(model, char_raws):
    char_raws = [0, *char_raws, 0] # add padding

    # raw character embeddings
    all_char_embeddings = model["s"].reshape(-1, 256)
    char_embeddings = all_char_embeddings[char_raws]
    
    # weighted character embeddings, needed so characters flow into each other
    all_char_embedding_weights = model["b"].reshape(-1, 256).T.reshape(256, 3, 256)
    sliding_window_embeddings = np.lib.stride_tricks.sliding_window_view(char_embeddings, (3, 256))
    weighted_embeddings = (sliding_window_embeddings * all_char_embedding_weights).sum(axis=2).sum(axis=2)
    weighted_embeddings += model["t"]
    weighted_embeddings = np.tanh(weighted_embeddings)

    char_embeddings = char_embeddings[1:-1] # strip padding 0 (see char_raws at the beginning of this function, each char has an embedding size of 256)
    
    concatenated_embeddings = np.concatenate((char_embeddings, weighted_embeddings), axis=1)

    intermediate = (concatenated_embeddings.reshape((-1, 512, 1)) * model["j"].reshape(1, 512, -1)).sum(axis=1)
    intermediate += model["E"]

    return intermediate

def sigmoid(arr):
    if arr.dtype == np.float32:
        arr = arr.clip(-88, None) # clip to avoid overflow in exp
    return 1 / (1 + np.exp(-arr))

def softplus(arr):
    if arr.dtype == np.float32:
        arr = arr.clip(None, 88) # clip to avoid overflow in exp
    return np.log(1 + np.exp(arr))

path_dir = os.path.abspath(os.path.dirname(__file__))
path_model = os.path.join(path_dir, "model.ulw")

class ModelULW(ModelRunner):
    name = "cai-ulw"
    writing_styles = [WritingStyle(i, f"Style {i}") for i in range(1, 10)]


    def load(self):
        self._model = parse_model(path_model)

    def invoke(self, text, biases, style):
        return run_model(self._model, text, style, biases, self.progress_cb)
