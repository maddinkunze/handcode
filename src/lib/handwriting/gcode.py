import os
import numpy as np
import tensorflow as tf
#from .rnn import rnn
#import tflite_runtime.interpreter as tflite
from .alphabet import alphabet as rnn_alphabet
from collections import defaultdict
from .savgol_np import savgol_filter

class HandGCode:
    settings_default = {
        "input": {
            "text": "Lorem ipsum"
        },
        "font": {
            "style": 1,
            "bias": 0.75,
            "size": 10,
            "lineheight": 15,
            "wordspacing": 7,
            "align": {
                "horizontal": 0,  # 0 -> left, 0.5 -> center, 1 -> right # TODO actually implement this feature
                "vertical": 0.8  # 0 -> top, 0.5 -> center, 1 -> bottom
            }
        },
        "page": {
            "width": 0,
            "height": 0,
            "rotate": 0
        },
        "commands": {
            "draw": {
                "start": None,
                "move": "G1 X{x:f} Y{y:f} Z0 F1000\n",
                "end": None
            },
            "travel": {
                "start": None,
                "move": "G1 X{x:f} Y{y:f} Z5 F1000\n",
                "end": None
            },
            "page": {
                "start": None,
                "next": "G1 Z50 F1000\nM0\n",
                "end": "G1 Z50 F1000\n"
            }
        },
        "output": {
            "file": "test.nc"
        },
        "features": {
            "replace": {      # automatically replace characters that are not supported (such as ä->a, ö->o, ü->u)
                "enabled": True
            },
            "imitate": {
                "enabled": False, # try to imitate special characters that are not supported (tries to draw two dots above an ä replaced by an a)
                "diaeresisasmacron": False # draw the dots above ä, ö, ü as two points (diaeresis, False) or one bar (macron, True)
            },
            "splitpages": {
                "enabled": False # when a page overflows instead of pausing the program, simply create another file
            }
        }
    }
    
    alphabet = rnn_alphabet
    replacements = {
        "Q": "O",
        "X": "x",
        "Z": "z",
        "Ä": "A",
        "Ö": "O",
        "Ü": "U",
        "ä": "a",
        "ö": "o",
        "ü": "u"
    }
    _alpha_to_num = defaultdict(int, list(map(reversed, enumerate(alphabet))))

    _directory = os.path.dirname(os.path.realpath(__file__))
    _cached_styles = {}

    def __init__(self, logger=print):
        """self._nn = rnn(
            log_dir=os.path.join(type(self)._directory, 'logs'),
            checkpoint_dir=os.path.join(type(self)._directory, 'checkpoints'),
            prediction_dir=os.path.join(type(self)._directory, 'predictions'),
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
        self._nn.restore()"""
        
        #self._model = tf.saved_model.load("/home/user/handcode/build/pbexport").signatures["classify"]
        pathDir = os.path.dirname(os.path.abspath(__file__))
        pathModel = os.path.join(pathDir, "model.tflite")
        self._model = tf.lite.Interpreter(pathModel).get_signature_runner("classify")
        
        self.logger = logger


    def generate(self, settings):
        passalong = dict()
        self.logger("Preprocessing input... ")
        self._preprocess(settings, passalong)
        self.logger("Done\nSample strokes... ")
        self._sample(settings, passalong)
        self.logger("Done\nDraw strokes... ")
        self._draw(settings, passalong)
        self.logger("Done\nAll Done!\n\n")

    def _preprocess(self, settings, passalong):
        settings_features = settings.get("features", {})
        settings_feature_replace = settings_features.get("replace", {})
        replace_enabled = settings_feature_replace.get("enabled", self.settings_default["features"]["replace"]["enabled"])
        settings_input = settings.get("input", {})
        text = settings_input.get("text", self.settings_default["input"]["text"])
        
        _ignore = "\n"
        _text = ""
        for c in text:
            _text += c
            if replace_enabled and (c not in self.alphabet) and (c not in self.replacements) and (c not in _ignore):
                _text += " "

        words = []
        newlines_before_words = []
        replacedcharacters = {}

        for line in _text.split("\n"):
            newlines_before_words.append(len(words))
            if not line:
                continue

            for word in line.split(" "):
                _word = ""
                _rchar = []
                for i, c in enumerate(word):
                    while replace_enabled and c and (c not in self.alphabet):
                        newc = self.replacements.get(c, "")
                        _rchar.append({"index": i, "old": c, "new": newc})
                        c = newc
                    _word += c
                    
                if _rchar:
                    replacedcharacters[len(words)] = _rchar
                words.append(_word)
        
        passalong["words"] = words
        passalong["newlines"] = newlines_before_words[1:]
        passalong["replacedcharacters"] = replacedcharacters

    @classmethod
    def _load_style(cls, style_name):
        cached_style = cls._cached_styles.get(style_name, None)
        if cached_style:
            return cached_style

        styles_path = os.path.join(cls._directory, "styles")
        strokes = np.load(os.path.join(styles_path, f"style-{style_name}-strokes.npy"))
        chars = np.load(os.path.join(styles_path, f"style-{style_name}-chars.npy"))

        cached_style = {"strokes": strokes, "chars": chars}
        cls._cached_styles[style_name] = cached_style
        return cached_style

    def _sample(self, settings, passalong):
        settings_font = settings.get("font", {})
        style = self._load_style(settings_font.get("style", self.settings_default["font"]["style"]))
        style_strokes = style["strokes"]
        style_strokes_len = len(style_strokes)
        style_chars = style["chars"]
        bias = settings_font.get("bias", self.settings_default["font"]["bias"])

        words = passalong["words"]
        words_len = len(words)
        
        prime = np.zeros([words_len, 1200, 3])
        prime_len = np.zeros([words_len])

        chars = np.zeros([words_len, 120])
        chars_len = np.zeros([words_len])

        biases = []
        tsteps_max = 0

        for i, word in enumerate(words):
            _chars = f"{style_chars.item().decode()} {word}"
            _chars = self._encode_ascii(_chars)
            _chars = np.array(_chars)

            prime[i, :style_strokes_len, :] = style_strokes
            prime_len[i] = style_strokes_len

            _chars_len = len(_chars)
            chars[i, :_chars_len] = _chars
            chars_len[i] = _chars_len

            biases.append(bias)
            if len(word) > tsteps_max:
                tsteps_max = len(word)
                
        """strokes = self._nn.session.run(
            [self._nn.sampled_sequence],
            feed_dict = {
                self._nn.prime: True,
                self._nn.x_prime: prime,
                self._nn.x_prime_len: prime_len,
                self._nn.num_samples: words_len,
                self._nn.sample_tsteps: 40*tsteps_max,
                self._nn.c: chars,
                self._nn.c_len: chars_len,
                self._nn.bias: biases
            }
        )[0]"""
        
        strokes = self._model(
            prime = tf.constant(True),
            x_prime = tf.constant(prime.astype("float32")),
            x_prime_len = tf.constant(prime_len.astype("int32")),
            num_samples = tf.constant(words_len),
            sample_tsteps = tf.constant(40 * tsteps_max),
            chars = tf.constant(chars.astype("int32")),
            chars_len = tf.constant(chars_len.astype("int32")),
            bias = tf.constant(biases)
        )["strokes"] # when using saved model instead of tflite, .numpy() should be called afterwards
        
        strokes = [stroke[~np.all(stroke == 0.0, axis=1)] for stroke in strokes]
        passalong["strokes"] = strokes 

    def _draw(self, settings, passalong):
        words = passalong["words"]
        strokes_words = passalong["strokes"]
        replacedcharacters = passalong["replacedcharacters"]

        settings_commands = settings.get("commands", {})
        commands_draw = settings_commands.get("draw", self.settings_default["commands"]["draw"])
        commands_travel = settings_commands.get("travel", self.settings_default["commands"]["travel"])
        settings_commands_page = settings_commands.get("page", {})
        command_page_start = settings_commands_page.get("start", self.settings_default["commands"]["page"]["start"])
        command_page_next = settings_commands_page.get("next", self.settings_default["commands"]["page"]["next"])
        command_page_end = settings_commands_page.get("end", self.settings_default["commands"]["page"]["end"])

        settings_font = settings.get("font", {})
        font_size = settings_font.get("size", self.settings_default["font"]["size"])
        font_line_height = settings_font.get("lineheight", self.settings_default["font"]["lineheight"])
        font_word_spacing = settings_font.get("wordspacing", self.settings_default["font"]["wordspacing"])
        settings_font_align = settings_font.get("align", {})
        font_align_vertical = settings_font_align.get("vertical", self.settings_default["font"]["align"]["vertical"]) # 0 -> top, 0.5 -> center, 1 -> baseline

        settings_page = settings.get("page", {})
        page_width = settings_page.get("width", self.settings_default["page"]["width"])
        page_height = settings_page.get("height", self.settings_default["page"]["height"])
        page_rotation = settings_page.get("rotate", self.settings_default["page"]["rotate"])
        page_rotation_rad = np.deg2rad(page_rotation)
        _pr_c, _pr_s = np.cos(page_rotation_rad), np.sin(page_rotation_rad)
        page_rotation_mat = np.array([[_pr_c, -_pr_s], [_pr_s, _pr_c]])

        settings_features = settings.get("features", {})
        settings_feature_imitate = settings_features.get("imitate", {})
        imitate_enabled = settings_feature_imitate.get("enabled", self.settings_default["features"]["imitate"]["enabled"])
        imitate_diaeresiasmacron = settings_feature_imitate.get("diaeresisasmacron", self.settings_default["features"]["imitate"]["diaeresisasmacron"])
        settings_feature_splitpages = settings_features.get("splitpages", {})
        splitpages_enabled = settings_feature_splitpages.get("enabled", self.settings_default["features"]["splitpages"]["enabled"])
        
        settings_output = settings.get("output", {})
        file_name = settings_output.get("file", self.settings_default["output"]["file"])
        file_index = 0
        file_out = open(file_name.format(part=file_index), "w")
        states = {
            "travel": commands_travel,
            "draw": commands_draw
        }
        if command_page_start:
            file_out.write(command_page_start)
        movegen = MoveGenerator(file_out, states, "travel")

        word_heights = []

        for i, word, strokes_word in zip(range(len(words)), words, strokes_words):
            if not strokes_word.size:
                continue

            if not word:
                strokes_words[i] = np.zeros((0, 3))
                continue
            
            strokes_word = self._offsets_to_coords(strokes_word)
            strokes_word = self._denoise(strokes_word)
            strokes_word[:, :2] = self._align(strokes_word[:, :2])

            strokes_word[:, 0] -= strokes_word[:, 0].min()
            strokes_word[:, 1] -= strokes_word[:, 1].max()

            word_height = -strokes_word[:, 1].min()
            strokes_word[:, 1] -= self._get_word_baseline_factor(word) * word_height
            word_height = -strokes_word[:, 1].min()
            word_heights.append(word_height)
            
            strokes_words[i] = strokes_word

        font_size_real = np.median(word_heights)
        size_factor = 1
        if font_size_real:
            size_factor = font_size / font_size_real
        newlines_before_words = passalong.get("newlines", [])
        _startposY = -font_align_vertical*(font_line_height-font_size)
        position_word = np.array([0., _startposY])

        for i, word, strokes_word in zip(range(len(words)), words, strokes_words):
            size_word = np.zeros(2)
            if strokes_word.size:
                strokes_word[:, :2] = strokes_word[:, :2] * size_factor
                size_word[0] = strokes_word[:, 0].max()
                size_word[1] = -strokes_word[:, 1].min()

                # check if we should insert a new line before this word (ie the word would overflow the page or the user entered a \n before the word)
                overflow_right = (page_width > 0) and ((position_word[0] + size_word[0]) > page_width)
                forced_newline = i in newlines_before_words
                if overflow_right or forced_newline:
                    position_word[0] = 0
                    for _i in range(max(1, newlines_before_words.count(i))):
                        position_word[1] -= font_line_height
                        # check if the line would overflow the page at the bottom
                        overflow_bottom = (page_height > 0) and ((-position_word[1])+font_line_height > page_height)
                        if overflow_bottom:
                            position_word[1] = _startposY
                            if splitpages_enabled:
                                if command_page_end:
                                    file_out.write(command_page_end)
                                file_out.close()

                                _file_name_prev = file_name.format(part=file_index)
                                file_index += 1
                                _file_name_next = file_name.format(part=file_index)
                                if _file_name_prev == _file_name_next:
                                    _file_name_next = list(os.path.splitext(file_name))
                                    _file_name_next[0] += f"-{file_index}"
                                    _file_name_next = "".join(_file_name_next)

                                file_out = open(_file_name_next, "w")
                                if command_page_start:
                                    file_out.write(command_page_start)
                                movegen = MoveGenerator(file_out, states, "travel")
                                
                            else:
                                file_out.write(command_page_pause)
                    

                # move the word to its correct position

                strokes_word[:, :2] += position_word


                # draw all strokes of the word itself and return to travel position afterwards

                state = None
                for stroke in strokes_word:
                    if stroke[2] > 0:
                        state = "travel"
                    else:
                        state = "draw"
                        
                    _move = np.dot(page_rotation_mat, stroke[:2])
                    movegen.move(state, x=_move[0], y=_move[1])
                movegen.move("travel", x=_move[0], y=_move[1])


            # get the distance to the following word

            word_spacing = font_word_spacing
            if callable(font_word_spacing):
                word_spacing = font_word_spacing()


            # imitate special characters such as ä, ö, ü, +, /
            
            rchars = replacedcharacters.get(i, [])
            if not imitate_enabled:
                rchars = []
            for rchar in rchars:
                _i = rchar["index"]
                _c = rchar["old"]

                _pos = self._estimate_character_position(word, _i)
                _pos *= np.array([size_word[0], -font_size])
                if _i >= len(word):
                    _pos[0] += 0.5 * word_spacing
                _pos += position_word
                _pos += 0.1 * (np.random.random(2) - 0.5) * font_size

                if _c in "ÄÖÜäöü":
                    _startpos = _pos + 0.1 * (np.random.random(2) - 0.5) * font_size
                    _startpos[0] -= 0.08 * font_size
                    _endpos = _pos + 0.1 * (np.random.random(2) - 0.5) * font_size
                    _endpos[0] += 0.08 * font_size

                    _move = np.dot(page_rotation_mat, _startpos)
                    movegen.move("travel", x=_move[0], y=_move[1])
                    movegen.move("draw", x=_move[0], y=_move[1])
                    if not imitate_diaeresiasmacron: # lift the pen when dots are required, leave it down if a bar should be drawn
                        _startpos += 0.05 * (np.random.random(2) - 0.5) * font_size
                        _move = np.dot(page_rotation_mat, _startpos)
                        movegen.move("travel", x=_move[0], y=_move[1])

                    _move = np.dot(page_rotation_mat, _endpos)
                    movegen.move("draw", x=_move[0], y=_move[1])
                    if not imitate_diaeresiasmacron:
                        _endpos += 0.05 * (np.random.random(2) - 0.5) * font_size
                    _move = np.dot(page_rotation_mat, _endpos)
                    movegen.move("travel", x=_move[0], y=_move[1])

                if _c == "+":
                    _startpos = _pos + 0.05 * (np.random.random(2) - np.array([0, 0.5])) * font_size
                    _startpos[1] += (0.3 + 0.3 * np.random.random()) * word_spacing
                    _endpos = _pos + 0.05 * (np.random.random(2) - np.array([1, 0.5])) * font_size
                    _endpos[1] -= (0.3 + 0.3 * np.random.random()) * word_spacing
                    _centerpos = (_startpos + _endpos) / 2 + 0.02 * (np.random.random(2) - 0.5) * font_size

                    _move = np.dot(page_rotation_mat, _startpos)
                    movegen.move("travel", x=_move[0], y=_move[1])
                    movegen.move("draw", x=_move[0], y=_move[1])
                    _move = np.dot(page_rotation_mat, _centerpos)
                    movegen.move("draw", x=_move[0], y=_move[1])
                    _move = np.dot(page_rotation_mat, _endpos)
                    movegen.move("travel", x=_move[0], y=_move[1])

                    _startpos = _pos + 0.05 * (np.random.random(2) - np.array([0.5, 0.8])) * font_size
                    _startpos[0] -= (0.3 + 0.3 * np.random.random()) * word_spacing
                    _endpos = _pos + 0.05 * (np.random.random(2) - np.array([0.5, 0.2])) * font_size
                    _endpos[0] += (0.3 + 0.3 * np.random.random()) * word_spacing
                    _centerpos = (_startpos + _endpos) / 2 + 0.02 * (np.random.random(2) - 0.5) * font_size
                    
                    _move = np.dot(page_rotation_mat, _startpos)
                    movegen.move("travel", x=_move[0], y=_move[1])
                    movegen.move("draw", x=_move[0], y=_move[1])
                    _move = np.dot(page_rotation_mat, _centerpos)
                    movegen.move("draw", x=_move[0], y=_move[1])
                    _move = np.dot(page_rotation_mat, _endpos)
                    movegen.move("travel", x=_move[0], y=_move[1])

                if _c == "/":
                    _startpos = _pos + 0.1 * (np.random.random(2) - np.array([0, 0.5])) * font_size
                    _startpos[0] += (0.3 + 0.3 * np.random.random()) * word_spacing
                    _startpos[1] += (0.3 + 0.3 * np.random.random()) * font_size
                    _endpos = _pos + 0.1 * (np.random.random(2) - np.array([1, 0.5])) * font_size
                    _endpos[0] -= (0.3 + 0.3 * np.random.random()) * word_spacing
                    _endpos[1] -= (0.3 + 0.3 * np.random.random()) * font_size
                    _centerpos = (_startpos + _endpos) / 2 + 0.02 * (np.random.random(2) - 0.5) * font_size

                    _move = np.dot(page_rotation_mat, _startpos)
                    movegen.move("travel", x=_move[0], y=_move[1])
                    movegen.move("draw", x=_move[0], y=_move[1])
                    _move = np.dot(page_rotation_mat, _centerpos)
                    movegen.move("draw", x=_move[0], y=_move[1])
                    _move = np.dot(page_rotation_mat, _endpos)
                    movegen.move("travel", x=_move[0], y=_move[1])

                if _c == "Q":
                    _startpos = _pos + 0.1 * (np.random.random(2) - 0.5) * font_size
                    _startpos[0] += (0.1 + 0.1 * np.random.random()) * font_size
                    _startpos[1] -= (0.55 + 0.1 * np.random.random()) * font_size
                    _endpos = _pos + 0.1 * (np.random.random(2) - 0.5) * font_size
                    _endpos[0] += (0.35 + 0.1 * np.random.random()) * font_size
                    _endpos[1] -= (0.8 + 0.1 * np.random.random()) * font_size
                    _centerpos = (_startpos + _endpos) / 2 + 0.02 * (np.random.random(2) - 1) * font_size
                    
                    _move = np.dot(page_rotation_mat, _startpos)
                    movegen.move("travel", x=_move[0], y=_move[1])
                    movegen.move("draw", x=_move[0], y=_move[1])
                    _move = np.dot(page_rotation_mat, _centerpos)
                    movegen.move("draw", x=_move[0], y=_move[1])
                    _move = np.dot(page_rotation_mat, _endpos)
                    movegen.move("travel", x=_move[0], y=_move[1])


            # advance to the next word position
            
            position_word[0] += size_word[0] + word_spacing

        if command_page_end:
            file_out.write(command_page_end)
        file_out.close()

    @classmethod
    def _encode_ascii(cls, ascii_string):
        """
        encodes ascii string to array of ints
        """
        return np.array(list(map(lambda x: cls._alpha_to_num[x], ascii_string)) + [0])

    @staticmethod
    def _denoise(coords):
        """
        smoothing filter to mitigate some artifacts of the data collection
        """
        coords = np.split(coords, np.where(coords[:, 2] == 1)[0] + 1, axis=0)
        new_coords = []
        for stroke in coords:
            if len(stroke) != 0:
                x_new = savgol_filter(stroke[:, 0], 7, 3, mode='nearest')
                y_new = savgol_filter(stroke[:, 1], 7, 3, mode='nearest')
                xy_coords = np.hstack([x_new.reshape(-1, 1), y_new.reshape(-1, 1)])
                stroke = np.concatenate([xy_coords, stroke[:, 2].reshape(-1, 1)], axis=1)
                new_coords.append(stroke)

        coords = np.vstack(new_coords)
        return coords

    @staticmethod
    def _offsets_to_coords(offsets):
        """
        convert from offsets to coordinates
        """
        return np.concatenate([np.cumsum(offsets[:, :2], axis=0), offsets[:, 2:3]], axis=1)

    @staticmethod
    def _align(coords):
        """
        corrects for global slant/offset in handwriting strokes
        """
        coords = np.copy(coords)
        X, Y = coords[:, 0].reshape(-1, 1), coords[:, 1].reshape(-1, 1)
        X = np.concatenate([np.ones([X.shape[0], 1]), X], axis=1)
        offset, slope = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(Y).squeeze()
        theta = np.arctan(slope)
        rotation_matrix = np.array(
            [[np.cos(theta), -np.sin(theta)],
             [np.sin(theta), np.cos(theta)]]
        )
        coords[:, :2] = np.dot(coords[:, :2], rotation_matrix) - offset
        return coords

    @staticmethod
    def _get_word_baseline_factor(word):
        word_top_max = 0.5
        word_top = 0
        word_middle = 1
        word_bottom = 0

        for c in "qpygj":
            if c in word:
                word_bottom = max(0.3, word_bottom)

        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZtdfhkl":
            if c in word:
                word_top = max(0.5, word_top)

        for c in "ij":
            if c in word:
                word_top = max(0.4, word_top)

        for c in "Q":
            if c in word:
                word_bottom = max(0.05, word_bottom)

        return (word_top_max - word_top) / (word_top + word_middle + word_bottom)

    @staticmethod
    def _estimate_character_position(word, index):
        _startend = 3
        width = _startend
        posX = _startend
        posY = 0
        
        for i, c in enumerate(word):
            _width = 10
            _height = 0
            if c in "ABCDEFGHKLNPRSTUVXYZ":
                _width = 16
                _height = 0.1
            if c in "IJ":
                _width = 11
                _height = 0.1
            if c in "MOW":
                _width = 26
                _height = 0.1
            if c in "abcdeghknpqsuvxyz":
                _width = 15
                _height = 0.3
            if c in "ftrlij":
                _width = 10
                _height = 0.3
            if c in "mow":
                _width = 25
                _height = 0.3
            if c in "()'":
                _width = 10
                _height = 0.5

            width += _width
            if i < index:
                posX += _width
            elif i == index:
                posX += _width / 2
                posY = _height

        if index >= len(word):
            posX += _startend
            posY = 0.6

        width += _startend
        if width:
            posX = posX/width
            
        return np.array([posX, posY])

class MoveGenerator:
    def __init__(self, file, states, default=None):
        self.file = file
        self.states = states
        self.state = default

    def move(self, state, **arguments):
        if state != self.state:
            self._callstate(self.state, "move", **arguments)
            self._callstate(self.state, "end", **arguments)
            self.state = state
            self._callstate(self.state, "start", **arguments)

        self._callstate(self.state, "move", **arguments)
        
    def _callstate(self, state, name, **arguments):
        current = self.states.get(self.state, None)
        if not current:
            return

        move = current.get(name, None)
        if not move:
            return

        self.file.write(move.format(**arguments))
