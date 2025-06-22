from itertools import chain
import random
import torch
from torch.distributions import MultivariateNormal, Bernoulli, Categorical
from torch.distributions.constraints import positive_definite
from .alphabet import character_map

torch.manual_seed(1023)

class OneHotEncoder:
    n_char = 57
    def one_hot(self, sentences):
        """
        Takes a list of setences and returns a list of torch tensors of the one-hot  
        encoded (char level) forms of the sentences.
        Arguments:
            sentences : list of strings (s)
        returns:
            one_hot_ : list of torch tensors of shapes (len(s), n_char)
        """
        sentences_idx = [
            torch.tensor([[character_map.get(c, self.n_char - 1)] for c in snt])
            for snt in sentences
        ]

        one_hot_ = [
            torch.zeros(idx_tnsr.shape[0], self.n_char).scatter_(
                dim=1, index=idx_tnsr, value=1.0
            )
            for idx_tnsr in sentences_idx
        ]
        return one_hot_

class HandWritingSynthRNN(torch.nn.Module):
    def __init__(
        self,
        memory_cells=400,
        n_gaussians=20,
        num_layers=2,
        n_gaussians_window=10,
        n_char=57,
        kappa_factor=0.05,
    ):
        """
        input_size is fixed to 3.
        hidden_size = memory_cells 
        Output dimension after the fully connected layer = (6 * n_gaussians + 1)
        """
        super().__init__()
        self.n_gaussians = n_gaussians
        self.n_gaussians_window = n_gaussians_window
        self.memory_cells = memory_cells
        self.n_char = n_char
        self.kappa_factor = kappa_factor
        self.first_rnn = torch.nn.LSTMCell(3 + n_char, memory_cells)
        self.rnns = torch.nn.ModuleList()
        input_size = 3 + memory_cells + n_char
        for i in range(num_layers - 1):
            self.rnns.append(torch.nn.LSTM(input_size, memory_cells, 1))

        self.h_to_w = torch.nn.Linear(
            in_features=memory_cells, out_features=3 * n_gaussians_window
        )
        # n_gaussians_window number of alpha, beta and kappa each

        self.last_layer = torch.nn.Linear(
            in_features=memory_cells * num_layers, out_features=(6 * n_gaussians + 1)
        )

    def forward(
        self, inp, c_seq, c_masks, lstm_in_states=None, prev_window=None, prev_kappa=0
    ):
        """
        first_layer of self.rnns gets inp as input
        subsequent layers of self.rnns get inp concatenated with output of
        previous layer as the input. 
        args: 
            inp: input sequence of dimensions (T, B, 3)
            c_seq: one-hot encoded and padded char sequence of 
                dimension (B, U, n_char)
            c_masks: 0 padded mask for c_seq with shape (B, U)
            lstm_in_states: input states for num_layers number of lstm 
                layers; it is a list of num_layers tupels (h_i, c_i), with
                both h_0 and c_0 tensor of dimensions (B, memory_cells)
                both h_i and c_i tensor of dimensions (T, B, memory_cells) for u > 0
            prev_window: (B, n_char)
            prev_kappa: (B, K=10, 1)
        """

        if prev_window is None:
            prev_window = inp.new_zeros(inp.shape[1], c_seq.shape[-1])  # (B, n_char)

        window_list = []
        first_rnn_out = []
        h, c = (
            [inp.new_zeros(inp.shape[1], self.memory_cells)] * 2
            if lstm_in_states is None
            else lstm_in_states[0]
        )
        attn_vars = {"phi_list": [], "kappa_list": []}
        for x in inp:
            rnn_inp = torch.cat((x, prev_window), dim=1)  # (B, 3+n_char)
            h, c = self.first_rnn(rnn_inp, (h, c))

            first_rnn_out.append(h)
            # Paramters for soft-window calculation
            window_params = self.h_to_w(h).exp()  # (B, 3*K)
            alpha, beta, kappa = window_params.unsqueeze(-1).chunk(chunks=3, dim=1)
            # shape : (B, K=10, 1); unsqueeze() for broadcasting into (B, K, U)
            kappa = prev_kappa + kappa * self.kappa_factor
            beta = -beta
            # Weights for soft-window calculation
            U = c_seq.shape[1]
            u_seq = torch.arange(1, U + 1).float().to(x.device)  # shape : (U)
            phi = ((beta * (kappa - u_seq) ** 2).exp() * alpha).sum(dim=1)  # (B, U)
            masked_phi = phi * c_masks  # Both of shape (B, U)

            attn_vars["kappa_list"].append(kappa.squeeze(dim=-1))  # (B, K)
            attn_vars["phi_list"].append(phi)  # (B, U)

            # shape: (B, n_char)
            prev_window = (masked_phi.unsqueeze(2) * c_seq).sum(dim=1)
            window_list.append(prev_window)
            prev_kappa = kappa

        # save the output and states of first_rnn (LSTMCell module) in
        # the format of returned value of an LSTM module
        # [(T, B, memory_cell)]
        rnn_out = [(torch.stack(first_rnn_out, dim=0), (h, c))]
        window = torch.stack(window_list, dim=0)  # (T, B, memory_cell)

        # Running rest of the rnn layers
        for i, rnn in enumerate(self.rnns):
            rnn_inp = torch.cat((rnn_out[-1][0], inp, window), dim=2)
            rnn_out.append(
                rnn(rnn_inp, lstm_in_states[i + 1])
                if lstm_in_states != None
                else rnn(rnn_inp)
            )

        # rnn_out is a list of tuples (out, (h, c))
        lstm_out_states = [o[1] for o in rnn_out]
        rnn_out = torch.cat([o[0] for o in rnn_out], dim=2)
        y = self.last_layer(rnn_out)

        log_pi = torch.log_softmax(y[:, :, : self.n_gaussians], dim=-1)
        mu = y[:, :, self.n_gaussians : 3 * self.n_gaussians]
        sigma = torch.exp(y[:, :, 3 * self.n_gaussians : 5 * self.n_gaussians])
        # sigma = y[:, :, 3*self.n_gaussians:5*self.n_gaussians]
        rho = torch.tanh(y[:, :, 5 * self.n_gaussians : 6 * self.n_gaussians])  # * 0.9
        e = torch.sigmoid(y[:, :, 6 * self.n_gaussians])

        return (
            e,
            log_pi,
            mu,
            sigma,
            rho,
            lstm_out_states,
            prev_window,
            prev_kappa,
            attn_vars,
        )

    def init_params(self):
        for param in chain(self.first_rnn.parameters(), self.rnns.parameters()):
            if param.dim() == 1:
                torch.nn.init.uniform_(param, -1e-2, 1e-2)
            else:
                torch.nn.init.orthogonal_(param)
        for param in chain(self.last_layer.parameters(), self.h_to_w.parameters()):
            if param.dim() == 1:
                torch.nn.init.uniform_(param, -1e-2, 1e-2)
            else:
                torch.nn.init.xavier_uniform_(param)

    def generate(self, sentences, bias, device, use_stopping):
        """
        Get handwritten form for given sentences
        arguments:
            sentences: List of one-hot encoded sentences (without padding)
        return:
            samples: tensor of handwritten form for the sentences
        """
        sentence_lens = [s.shape[0] for s in sentences]
        # print(sentence_lens)

        # pad sentences (B, U, n_char) and create generate c_masks
        c_seq = torch.nn.utils.rnn.pad_sequence(
            sentences, batch_first=True, padding_value=0.0
        )
        batch, U, n_char = c_seq.shape

        if use_stopping:
            # add couple of dummy 0s at end sentences (U = U + 2; will help for termication condition)
            c_seq = torch.cat((c_seq, c_seq.new_zeros(batch, 2, n_char)), dim=1)
            U = U + 2

        c_masks = torch.zeros(batch, U, device=device)
        for i, s in enumerate(sentences):
            c_masks[i][: s.shape[0]] = 1

        max_length = 600
        if use_stopping:
            max_length = 1000
        # empty matrix of required shape with batch_first = False
        samples = torch.empty(max_length + 1, batch, 3, device=device)
        lstm_states = None
        window = torch.zeros(batch, n_char, device=device)
        kappa = torch.zeros(batch, self.n_gaussians_window, 1, device=device)

        attn_vars = {"phi_list": [], "kappa_list": []}

        for i in range(1, max_length + 1):
            # get distribution parameters
            with torch.no_grad():
                e, log_pi, mu, sigma, rho, lstm_states, window, kappa, attn_vars_i = self.forward(
                    samples[i - 1 : i], c_seq, c_masks, lstm_states, window, kappa
                )

            # implement stopping criteria
            if use_stopping:
                end_loop = True
                strokes_mask = samples.new_zeros(batch)
                phi = attn_vars_i["phi_list"][-1]
                for j, l in enumerate(sentence_lens):
                    max_phi_idx = phi[j].argmax()
                    if max_phi_idx <= l:
                        end_loop = False
                        strokes_mask[j] = 1.0
                # keeping at lower limit of stroke sequence to 20
                if i > 20 and end_loop:
                    break

            mu.nan_to_num(mu.nanmean())

            attn_vars["phi_list"] += attn_vars_i["phi_list"]
            attn_vars["kappa_list"] += attn_vars_i["kappa_list"]

            # sample from the distribution (returned parameters)
            # samples[i, :, 0] = e[-1, :] > 0.5
            distrbn1 = Bernoulli(e[-1, :].nan_to_num(0))
            samples[i, :, 0] = distrbn1.sample()

            # selected_mode = torch.argmax(log_pi[-1, :, :], dim=1) # shape = (batch,)
            distrbn2 = Categorical((log_pi[-1, :, :].nan_to_num(0) * (1 + bias)).exp())
            selected_mode = distrbn2.sample()

            index_1 = selected_mode.unsqueeze(1)  # shape (batch, 1)
            # shape (batch, 1, 2)
            index_2 = torch.stack([index_1, index_1], dim=2)

            mu = (
                mu[-1]
                .view(batch, self.n_gaussians, 2)
                .gather(dim=1, index=index_2)
                .squeeze(dim=1)
            )
            sigma = (
                (sigma[-1] / torch.exp(torch.tensor(1 + bias)))
                .view(batch, self.n_gaussians, 2)
                .gather(dim=1, index=index_2)
                .squeeze(dim=1)
            )
            rho = rho[-1].gather(dim=1, index=index_1).squeeze(dim=1)

            sigma2d = sigma.new_zeros(batch, 2, 2)
            sigma2d[:, 0, 0] = sigma[:, 0] ** 2
            sigma2d[:, 1, 1] = sigma[:, 1] ** 2
            sigma2d[:, 0, 1] = rho[:] * sigma[:, 0] * sigma[:, 1]
            sigma2d[:, 1, 0] = sigma2d[:, 0, 1]
            sigma2d = sigma2d.nan_to_num(sigma2d.nanmean())
            
            distribn = MultivariateNormal(loc=mu, covariance_matrix=sigma2d)
            
            samples[i, :, 1:] = distribn.sample()
            if use_stopping:
                samples[i, :, :] *= strokes_mask.unsqueeze(-1)

        return samples[1:, :, :]
