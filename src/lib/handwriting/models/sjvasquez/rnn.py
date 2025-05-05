from __future__ import print_function
import os

import numpy as np
import tensorflow as tf
#tf.compat.v1.disable_v2_behavior()

from .alphabet import character_map
from .rnn_cell import LSTMAttentionCell
from .rnn_ops import rnn_free_run
from .tf_base_model import TFBaseModel
from .tf_utils import time_distributed_dense_layer


class rnn(TFBaseModel):

    def __init__(
        self,
        lstm_size,
        output_mixture_components,
        attention_mixture_components,
        **kwargs
    ):
        self.lstm_size = lstm_size
        self.output_mixture_components = output_mixture_components
        self.output_units = self.output_mixture_components*6 + 1
        self.attention_mixture_components = attention_mixture_components
        super(rnn, self).__init__(**kwargs)

    def parse_parameters(self, z, eps=1e-8, sigma_eps=1e-4):
        pis, sigmas, rhos, mus, es = tf.split(
            z,
            [
                1*self.output_mixture_components,
                2*self.output_mixture_components,
                1*self.output_mixture_components,
                2*self.output_mixture_components,
                1
            ],
            axis=-1
        )
        pis = tf.nn.softmax(pis, axis=-1)
        sigmas = tf.clip_by_value(tf.exp(sigmas), sigma_eps, np.inf)
        rhos = tf.clip_by_value(tf.tanh(rhos), eps - 1.0, 1.0 - eps)
        es = tf.clip_by_value(tf.nn.sigmoid(es), eps, 1.0 - eps)
        return pis, mus, sigmas, rhos, es

    def NLL(self, y, lengths, pis, mus, sigmas, rho, es, eps=1e-8):
        sigma_1, sigma_2 = tf.split(sigmas, 2, axis=2)
        y_1, y_2, y_3 = tf.split(y, 3, axis=2)
        mu_1, mu_2 = tf.split(mus, 2, axis=2)

        norm = 1.0 / (2*np.pi*sigma_1*sigma_2 * tf.sqrt(1 - tf.square(rho)))
        Z = tf.square((y_1 - mu_1) / (sigma_1)) + \
            tf.square((y_2 - mu_2) / (sigma_2)) - \
            2*rho*(y_1 - mu_1)*(y_2 - mu_2) / (sigma_1*sigma_2)

        exp = -1.0*Z / (2*(1 - tf.square(rho)))
        gaussian_likelihoods = tf.exp(exp) * norm
        gmm_likelihood = tf.reduce_sum(input_tensor=pis * gaussian_likelihoods, axis=2)
        gmm_likelihood = tf.clip_by_value(gmm_likelihood, eps, np.inf)

        bernoulli_likelihood = tf.squeeze(tf.where(tf.equal(tf.ones_like(y_3), y_3), es, 1 - es))

        nll = -(tf.math.log(gmm_likelihood) + tf.math.log(bernoulli_likelihood))
        sequence_mask = tf.logical_and(
            tf.sequence_mask(lengths, maxlen=tf.shape(input=y)[1]),
            tf.logical_not(tf.math.is_nan(nll)),
        )
        nll = tf.where(sequence_mask, nll, tf.zeros_like(nll))
        num_valid = tf.reduce_sum(input_tensor=tf.cast(sequence_mask, tf.float32), axis=1)

        sequence_loss = tf.reduce_sum(input_tensor=nll, axis=1) / tf.maximum(num_valid, 1.0)
        element_loss = tf.reduce_sum(input_tensor=nll) / tf.maximum(tf.reduce_sum(input_tensor=num_valid), 1.0)
        return sequence_loss, element_loss

    def sample(self, cell):
        initial_state = cell.zero_state(self.num_samples, dtype=tf.float32)
        initial_input = tf.concat([
            tf.zeros([self.num_samples, 2]),
            tf.ones([self.num_samples, 1]),
        ], axis=1)
        return rnn_free_run(
            cell=cell,
            sequence_length=self.sample_tsteps,
            initial_state=initial_state,
            initial_input=initial_input,
            scope='rnn'
        )[1]

    def primed_sample(self, cell):
        initial_state = cell.zero_state(self.num_samples, dtype=tf.float32)
        primed_state = tf.compat.v1.nn.dynamic_rnn(
            inputs=self.x_prime,
            cell=cell,
            sequence_length=self.x_prime_len,
            dtype=tf.float32,
            initial_state=initial_state,
            scope='rnn'
        )[1]
        return rnn_free_run(
            cell=cell,
            sequence_length=self.sample_tsteps,
            initial_state=primed_state,
            scope='rnn'
        )[1]

    def calculate_loss(self):
        self.x = tf.compat.v1.placeholder(tf.float32, [None, None, 3])
        self.y = tf.compat.v1.placeholder(tf.float32, [None, None, 3])
        self.x_len = tf.compat.v1.placeholder(tf.int32, [None])
        self.c = tf.compat.v1.placeholder(tf.int32, [None, None])
        self.c_len = tf.compat.v1.placeholder(tf.int32, [None])

        self.sample_tsteps = tf.compat.v1.placeholder(tf.int32, [])
        self.num_samples = tf.compat.v1.placeholder(tf.int32, [])
        self.prime = tf.compat.v1.placeholder(tf.bool, [])
        self.x_prime = tf.compat.v1.placeholder(tf.float32, [None, None, 3])
        self.x_prime_len = tf.compat.v1.placeholder(tf.int32, [None])
        self.bias = tf.compat.v1.placeholder_with_default(
            tf.zeros([self.num_samples], dtype=tf.float32), [None])

        cell = LSTMAttentionCell(
            lstm_size=self.lstm_size,
            num_attn_mixture_components=self.attention_mixture_components,
            attention_values=tf.one_hot(self.c, len(character_map)),
            attention_values_lengths=self.c_len,
            num_output_mixture_components=self.output_mixture_components,
            bias=self.bias
        )
        self.initial_state = cell.zero_state(tf.shape(input=self.x)[0], dtype=tf.float32)
        outputs, self.final_state = tf.compat.v1.nn.dynamic_rnn(
            inputs=self.x,
            cell=cell,
            sequence_length=self.x_len,
            dtype=tf.float32,
            initial_state=self.initial_state,
            scope='rnn'
        )
        params = time_distributed_dense_layer(outputs, self.output_units, scope='rnn/gmm')
        pis, mus, sigmas, rhos, es = self.parse_parameters(params)
        sequence_loss, self.loss = self.NLL(self.y, self.x_len, pis, mus, sigmas, rhos, es)

        self.sampled_sequence = tf.cond(
            pred=self.prime,
            true_fn=lambda: self.primed_sample(cell),
            false_fn=lambda: self.sample(cell)
        )
        return self.loss
