# This file is part of auditory_models
# Copyright (C) 2025 Max Zimmermann
#
# auditory_models is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# auditory_models is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with auditory_models.  If not, see <https://www.gnu.org/licenses/>.


import functools

import numpy as np
from numpy.typing import ArrayLike, NDArray, DTypeLike
from scipy.signal import resample_poly
from typing import TypeVar
from warnings import warn

EPS = np.finfo("float").eps


# ERB means "Equivalent retangular band(-width)"
# Constants:
_ERB_L = 24.7
_ERB_Q = 9.265


float_or_array = TypeVar("float_or_array", float, NDArray)


class ResampleOct:
    """
    This class shall construct a resampling window based on a current and target sampling frequency. Then this window
    shall be used in the process function to resample data in a numpy array.

    # Acknowledgment
        This class is a modified version from the pystoi implementation by Manuel Pariente
        (https://github.com/mpariente/pystoi), for previous licensing see file LICENSE.old in src/auditory_models/stoi
    """
    def __init__(self, target_fs: int = None, current_fs: int = None):
        self._target_fs = None
        self._current_fs = None
        self._target_fs_reduced = None
        self._current_fs_reduced = None
        self.window = None
        self.target_fs = target_fs
        self.current_fs = current_fs

    @property
    def target_fs(self):
        return self._target_fs

    @target_fs.setter
    def target_fs(self, value: int):
        if self._target_fs != value:
            self._target_fs = value
            if self._current_fs:
                self._reduce_fs()

    @property
    def current_fs(self):
        return self._current_fs

    @current_fs.setter
    def current_fs(self, value: int):
        if self._current_fs != value:
            self._current_fs = value
            if self._target_fs:
                self._reduce_fs()

    def _reduce_fs(self) -> None:
        """
        Method to recalculate the reduced sampling frequencies an the resampling window on change of a sampling
        frequency.
        :return: None
        """
        gcd = np.gcd(self._target_fs, self._current_fs)
        if gcd > 1:
            self._target_fs_reduced = int(self.target_fs / gcd)
            self._current_fs_reduced = int(self.current_fs / gcd)
        self.resample_window_oct()

    def resample_window_oct(self) -> None:
        """
        Port of Octave code to Python. Create a resampling window.
        """

        # Properties of the antialiasing filter
        log10_rejection = -3.0
        stopband_cutoff_f = 1.0 / (2 * max(self._target_fs_reduced, self._current_fs_reduced))
        roll_off_width = stopband_cutoff_f / 10

        # Determine filter length
        rejection_dB = -20 * log10_rejection
        L = np.ceil((rejection_dB - 8) / (28.714 * roll_off_width))

        # Ideal sinc filter
        t = np.arange(-L, L + 1)
        ideal_filter = 2 * self._target_fs_reduced * stopband_cutoff_f \
            * np.sinc(2 * stopband_cutoff_f * t)

        # Determine parameter of Kaiser window
        if (rejection_dB >= 21) and (rejection_dB <= 50):
            beta = 0.5842 * (rejection_dB - 21)**0.4 \
                + 0.07886 * (rejection_dB - 21)
        elif rejection_dB > 50:
            beta = 0.1102 * (rejection_dB - 8.7)
        else:
            beta = 0.0

        # Apodize ideal filter response
        h = np.kaiser(2 * L + 1, beta) * ideal_filter
        self.window = h / np.sum(h)

    def process(self, in_sig: np.ndarray, axis: int = 0) -> np.ndarray:
        """Resampler that is compatible with Octave"""
        if len(in_sig.shape) > 2:
            warn("The signal's shape has more than 2 dimensions.")
        if np.argmax(in_sig.shape) != axis:
            warn(f"The signal's shape is {in_sig.shape} and resampling will execute along axis {axis}.")
        out_sig = resample_poly(in_sig, self.target_fs, self.current_fs, window=self.window, axis=axis)
        return out_sig


@functools.lru_cache(maxsize=None)
def thirdoct(fs: float | int, nfft: int, min_freq: int = 0, max_freq: int | None = None):
    """
    Returns the 1/3 octave band matrix and its center frequencies. Values for center frequencies are as defined by
    IEC 61260-1:2014.
    # Arguments :
        fs : sampling rate
        nfft : FFT size
        min_freq : only bands with a center frequency of min_freq or higher are included
        max_freq : only bands with a center frequency of max_freq or lower are included
    # Returns :
        obm : Octave Band Matrix with shape=(number of bands, nfft/2+1)
        cf : center frequencies
    # Acknowledgment
        This function is a modified version from the pystoi implementation by Manuel Pariente
        (https://github.com/mpariente/pystoi), for previous licensing see file LICENSE.old in src/auditory_models/stoi
    """
    if not max_freq:
        max_freq = round(fs / 2)
    nfft2 = round(nfft / 2 + 1)
    nominal_cf = np.array([
        25, 31.5, 40, 50, 63, 80, 100, 125, 160,
        200, 250, 315, 400, 500, 630, 800, 1000,
        1250, 1600, 2000, 2500, 3150, 4000, 5000,
        6300, 8000, 10000, 12500, 16000, 20000], dtype=int)
    trimming = np.logical_and(nominal_cf <= max_freq, nominal_cf >= min_freq)
    cf = nominal_cf[trimming].astype(float)
    f_high = cf * 2 ** (1/6)
    f_low = np.concatenate((np.array([cf[0] * 2 ** (-1/6)]), f_high[:-1]))
    f_high = f_high.reshape((f_high.size, 1))
    f_low = f_low.reshape((f_low.size, 1))
    freq_bins = np.linspace(0, fs / 2, nfft2).reshape((1, nfft2))
    # generate a matrix with rows = number of bands and columns = number of freq-bins via matrix comparison of a column
    # vector (f_high and f_low, respectively) with a row vector (f)
    obm = np.logical_and(f_high >= freq_bins, f_low <= freq_bins).astype(float)
    return obm, cf


def _overlap_and_add(x_frames: np.ndarray, hop: int):
    """
    Perform an overlap-add procedure on a matrix of frames with a given hop-size to reconstruct the signal.
    :param x_frames: matrix of frames, axis 0: number of frames, axis 1: frame length
    :param hop: hop-size
    :return: complete reconstructed signal
    """
    num_frames, framelen = x_frames.shape
    # Compute the number of segments, per frame.
    segments = round(np.ceil(framelen / hop))  # Divide and round up.

    # Pad the framelen dimension to segments * hop and add n=segments frames
    signal = np.pad(x_frames, ((0, segments), (0, segments * hop - framelen)))

    # Reshape to a 3D tensor, splitting the framelen dimension in two
    signal = signal.reshape((num_frames + segments, segments, hop))
    # Transpose dimensions so that signal.shape = (segments, frame+segments, hop)
    signal = np.transpose(signal, [1, 0, 2])
    # Reshape so that signal.shape = (segments * (frame+segments), hop)
    signal = signal.reshape((-1, hop))

    # Now behold the magic!! Remove the last n=segments elements from the first axis
    signal = signal[:-segments]
    # Reshape to (segments, frame+segments-1, hop)
    signal = signal.reshape((segments, num_frames + segments - 1, hop))
    # This has introduced a shift by one in all rows

    # Now, reduce over the columns and flatten the array to achieve the result
    signal = np.sum(signal, axis=0)
    end = (len(x_frames) - 1) * hop + framelen
    signal = signal.reshape(-1)[:end]
    return signal


def remove_silent_frames(x: np.ndarray, y: np.ndarray, dyn_range: int | float, framelen: int, hop: int):
    """
    Remove silent frames of x and y based on x
    A frame is excluded if its energy is lower than max(energy) - dyn_range
    The frame exclusion is based solely on x, the clean speech signal
    # Arguments :
        x : array, original speech wav file
        y : array, denoised speech wav file
        dyn_range : Energy range to determine which frame is silent
        framelen : Window size for energy evaluation
        hop : Hop size for energy evaluation
    # Returns :
        x without the silent frames
        y without the silent frames
    """
    # Compute Mask
    w = np.hanning(framelen + 2)[1:-1]

    x_frames = np.array(
        [w * x[i:i + framelen] for i in range(0, len(x) - framelen + 1, hop)])
    y_frames = np.array(
        [w * y[i:i + framelen] for i in range(0, len(x) - framelen + 1, hop)])

    # Compute energies in dB
    x_energies = 20 * np.log10(np.linalg.norm(x_frames, axis=1) + EPS)

    # Find boolean mask of energies lower than dynamic_range dB
    # with respect to maximum clean speech energy frame
    mask = (np.max(x_energies) - dyn_range - x_energies) < 0

    # Remove silent frames by masking
    x_sil = _overlap_and_add(x_frames[mask, :], hop)
    y_sil = _overlap_and_add(y_frames[mask, :], hop)

    # rebuild the trailing beginning and end by division by the respective part of the window function
    x_sil[0:hop] /= w[0:hop]
    x_sil[-hop::] /= w[-hop::]
    y_sil[0:hop] /= w[0:hop]
    y_sil[-hop::] /= w[-hop::]

    return x_sil, y_sil


def iso389_7_thresholds(desired_freqs: NDArray, field: str = "free") -> NDArray:
    """
    Linear interpolation of calibration thresholds taken from "ISO 389-7 Akustik - Standard-Bezugspegel für die
    Kalibrierung von audiometrischen Geräten - Teil 7: Bezugshörschwellen unter Freifeld- und Diffusfeldbedingungen".
    :param desired_freqs: frequencies in Hz for which the respective threshold values shall be interpolated, values
        must be ordered ascending
    :param field: sound field conditions, must be either "free" or "diffuse"
    :return: array containing the interpolated thresholds in dB for the frequencies defined in `desired_freqs`
    """
    thresholds = np.array([[20., 78.1, 78.1],
                           [25., 68.7, 68.7],
                           [31.5, 59.5, 59.5],
                           [40., 51.1, 51.1],
                           [50., 44.0, 44.0],
                           [63., 37.5, 37.5],
                           [80., 31.5, 31.5],
                           [100., 26.5, 26.5],
                           [125., 22.1, 22.1],
                           [160., 17.9, 17.9],
                           [200., 14.4, 14.4],
                           [250., 11.4, 11.4],
                           [315., 8.6, 8.4],
                           [400., 6.2, 5.8],
                           [500., 4.4, 3.8],
                           [630., 3.0, 2.1],
                           [750., 2.4, 1.2],
                           [800., 2.2, 1.0],
                           [1000., 2.4, 0.8],
                           [1250., 3.5, 1.9],
                           [1500., 2.4, 1.0],
                           [1600., 1.7, 0.5],
                           [2000., -1.3, -1.5],
                           [2500., -4.2, -3.1],
                           [3000., -5.8, -4.0],
                           [3150., -6.0, -4.0],
                           [4000., -5.4, -3.8],
                           [5000., -1.5, -1.8],
                           [6000., 4.3, 1.4],
                           [6300., 6.0, 2.5],
                           [8000., 12.6, 6.8],
                           [9000., 13.9, 8.4],
                           [10000., 13.9, 9.8],
                           [11200., 13.0, 11.5],
                           [12500., 12.3, 14.4],
                           [14000., 18.4, 23.2],
                           [16000., 40.2, 43.7],
                           [18000., 70.4, 43.7]])
    if field == "free":
        col = 1
    elif field == "diffuse":
        col = 2
    else:
        raise ValueError(f"`field` must be either 'free' or 'diffuse', currently: {field}")
    return np.interp(desired_freqs, thresholds[:, 0], thresholds[:, col])


def generate_delta_impulse(num_samples: int, dtype: DTypeLike = np.float64) -> NDArray:
    """
    Generate a delta impulse (array of zeros with a one as first element).
    :param num_samples: length of signal in samples
    :param dtype: data type of array content
    :return: array with delta impulse
    """
    sig = np.zeros(num_samples, dtype=dtype)
    sig[0] = 1.0
    return sig


def erb_count(cf: float_or_array) -> float_or_array:
    """
    Returns the equivalent rectangular band count up to center-frequency.
    :param cf: The center frequency in Hz of the desired auditory filter.
    :return: Number of equivalent bandwidths below `cf`
    """
    return 21.4 * np.log10(4.37 * 0.001 * cf + 1)


def erb_aud(cf: float_or_array) -> float_or_array:
    """
    Returns equivalent rectangular bandwidth of an auditory filter. Implements Equation 13 im [Hohmann2002].
    :param cf: The center frequency in Hz of the desired auditory filter.
    :return: Equivalent rectangular bandwidth of an auditory filter at `cf`
    """
    return _ERB_L + cf / _ERB_Q


def hertz_to_erbscale(freq: float_or_array) -> float_or_array:
    """
    Returns ERB-frequency from frequency in Hz. Implements Equation 16 in [Hohmann2002].
    :param freq: frequency in Hz
    :return: The corresponding value on the ERB-Scale.
    """
    return _ERB_Q * np.log(1 + freq / (_ERB_L * _ERB_Q))


def erbscale_to_hertz(erb: float_or_array) -> float_or_array:
    """
    Returns frequency in Hertz from ERB value. Implements Equation 17 in [Hohmann2002].
    :param erb: The corresponding value on the ERB-Scale.
    :return: The Frequency in Hz.
    """
    return (np.exp(erb / _ERB_Q) - 1) * _ERB_L * _ERB_Q


def freq_erb_spaced(start_band: int, end_band: int, norm_freq: float, density: float) -> NDArray:
    """
    Returns frequencies in ERB spacing.
    :param start_band: ERB counts below `norm_freq`
    :param end_band: ERB count above `norm_freq`
    :param norm_freq: The reference frequency where all filters are around
    :param density: ERB density of 1 would be `erb_aud`
    :return: array of ERB-spaced frequencies
    """
    return erbscale_to_hertz(np.arange(start_band, end_band, density) + hertz_to_erbscale(norm_freq))
