from .rnn import rnn
from .model_base import BaseTFModel, path_checkpoints

class ModelRNN(BaseTFModel):
    name = "hws-rnn"

    def load(self):
        self._model = rnn(
            checkpoint_dir=path_checkpoints,
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
        self._model.restore()

    def invoke(self, text, biases, style):
        words_len, prime, prime_len, chars, chars_len, tsteps_max = self._prepare_inputs(text, style)

        return self._model.session.run(
            [self._model.sampled_sequence],
            feed_dict = {
                self._model.prime: True,
                self._model.x_prime: prime,
                self._model.x_prime_len: prime_len,
                self._model.num_samples: words_len,
                self._model.sample_tsteps: tsteps_max,
                self._model.c: chars,
                self._model.c_len: chars_len,
                self._model.bias: biases
            }
        )[0].numpy()
