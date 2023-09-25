import numpy as np

# based on savgol implementation of scipy

def savgol_coeffs(window_length, polyorder, pos=None,
                  use="conv"):

    if polyorder >= window_length:
        raise ValueError("polyorder must be less than window_length.")

    halflen, rem = divmod(window_length, 2)

    if pos is None:
        if rem == 0:
            pos = halflen - 0.5
        else:
            pos = halflen

    if not (0 <= pos < window_length):
        raise ValueError("pos must be nonnegative and less than "
                         "window_length.")

    if use not in ['conv', 'dot']:
        raise ValueError("`use` must be 'conv' or 'dot'")

    # Form the design matrix A. The columns of A are powers of the integers
    # from -pos to window_length - pos - 1. The powers (i.e., rows) range
    # from 0 to polyorder. (That is, A is a vandermonde matrix, but not
    # necessarily square.)
    x = np.arange(-pos, window_length - pos, dtype=float)

    if use == "conv":
        # Reverse so that result can be used in a convolution.
        x = x[::-1]

    order = np.arange(polyorder + 1).reshape(-1, 1)
    A = x ** order

    # y determines which order derivative is returned. -> simplified due to deriv==0
    y = np.zeros(polyorder + 1)
    y[0] = 1

    # Find the least-squares solution of A*c = y
    coeffs, _, _, _ = np.linalg.lstsq(A, y, rcond=None)

    return coeffs


def savgol_filter(x, window_length, polyorder, mode='interp'):
    if mode not in ["mirror", "constant", "nearest", "interp", "wrap"]:
        raise ValueError("mode must be 'mirror', 'constant', 'nearest' "
                         "'wrap' or 'interp'.")

    x = np.asarray(x)
    # Ensure that x is either single or double precision floating point.
    if x.dtype != np.float64 and x.dtype != np.float32:
        x = x.astype(np.float64)

    coeffs = savgol_coeffs(window_length, polyorder)

    # Any mode other than 'interp' is passed on to ndimage.convolve1d (-> replaced with np.convolve).
    # condition removed since savgol_filter will only ever be called with mode=="nearest"
    if mode == "nearest":
        x = np.pad(x, window_length//2, mode="edge")
        mode = "valid"
    y = np.convolve(x, coeffs, mode=mode)

    return y
