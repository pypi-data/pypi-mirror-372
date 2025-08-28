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


import numpy as np
from scipy.signal import stft
import warnings

from auditory_models.helpers import utils


class STOI:
    def __init__(self, fs: int = 10000, block_size: int = 256, nfft: int = 512, min_freq: int = 150,
                 max_freq: int | None = None, n_segmentation: int = 30, beta: float = -15.0, dyn_range: float = 40.0,
                 variation: str = 'classic') -> None:
        """
        Short term objective intelligibility
        Computes the STOI (See [1][2]) of a denoised signal compared to a clean
        signal, The output is expected to have a monotonic relation with the
        subjective speech-intelligibility, where a higher score denotes better
        speech intelligibility.
        ==NOTE!==: There are some changes in this implementation that differ from the original:
            1)
            The third-octave bands now have fixed center frequencies (as defined by IEC 61260-1:2014) that do not
            change with 'min_freq'. The number of bands is determined by 'min_freq', which defines the lowest possible
            center frequency and 'max_freq', which defines the highest possible center frequency. If 'max_freq' is not
            provided, it will default to the Nyquist-frequency.
        :param fs: Sampling frequency
        :param block_size: Block size in samples for STFT
        :param nfft: Number of FFT-bins per block
        :param min_freq: Minimum center frequency of third octave bands
        :param max_freq: Maximum center frequency of third octave bands
        :param n_segmentation: Number of blocks that will be grouped together
        :param beta: Lower signal-to-distortion bound
        :param dyn_range: Dynamic range with respect to the block with maximum energy. All blocks below that range are
        treated as silent and will be removed from further computation.
        :param variation: Denotes which computational variation shall be used. Currently available:
            - classic: Implementation as presented by Taal et al.
            - pre-mean: return the correlation matrix before computing the mean in eq. 6
        """
        self._fs = fs
        self._block_size = block_size
        self._nfft = nfft
        self._min_freq = min_freq
        self._max_freq = np.min((max_freq, round(self._fs / 2))) if max_freq else round(self._fs / 2)
        # Get 1/3 octave band matrix
        self._obm, self._cf = utils.thirdoct(self._fs, self._nfft, min_freq=self._min_freq, max_freq=self._max_freq)
        self._n_segmentation = n_segmentation
        self._beta = beta
        self._dyn_range = dyn_range
        self._variation = variation
        self.resampler = utils.ResampleOct(target_fs=self._fs)
        self.name = "STOI"
        self.unit = ""

    def process(self, x: np.ndarray, y: np.ndarray, fs_sig: int) -> float | np.ndarray:
        """
        Compute the STOI from two input signals and their sampling frequency.

        :param x: clean original speech
        :param y: denoised speech
        :param fs_sig: sampling rate of x and y
        :return: float: Short time objective intelligibility measure between clean and denoised speech
            np.ndarray of floats if `variation`="pre-mean"

        # Raises
            AssertionError : if x and y have different lengths

        # Reference
            [1] C.H.Taal, R.C.Hendriks, R.Heusdens, J.Jensen 'A Short-Time
                Objective Intelligibility Measure for Time-Frequency Weighted Noisy
                Speech', ICASSP 2010, Texas, Dallas.
            [2] C.H.Taal, R.C.Hendriks, R.Heusdens, J.Jensen 'An Algorithm for
                Intelligibility Prediction of Time-Frequency Weighted Noisy Speech',
                IEEE Transactions on Audio, Speech, and Language Processing, 2011.

        # Acknowledgment
            This method is a modified version from the pystoi implementation by Manuel Pariente
            (https://github.com/mpariente/pystoi), for previous licensing see file LICENSE.old in the same directory as
            this file.
        """
        assert x.shape == y.shape, f"x and y should have the same length, found {x.shape} and {y.shape}"
        assert len(x.shape) == 1, f"STOI is made for single channel audio, array of shape {x.shape} entered..."

        # Resample if fs_sig is different from fs
        if fs_sig != self._fs:
            self.resampler.current_fs = fs_sig
            x = self.resampler.process(x)
            y = self.resampler.process(y)

        # Remove silent frames
        x, y = utils.remove_silent_frames(x, y, self._dyn_range, self._block_size, round(self._block_size / 2))

        # Take STFT
        x_spec = stft(x, fs=self._fs, window="hann", nperseg=self._block_size, nfft=self._nfft, axis=0)[2]
        y_spec = stft(y, fs=self._fs, window="hann", nperseg=self._block_size, nfft=self._nfft, axis=0)[2]

        # Ensure at least 30 frames for intermediate intelligibility
        if x_spec.shape[-1] < self._n_segmentation:
            warnings.warn("Not enough STFT frames to compute intermediate "
                          "intelligibility measure after removing silent "
                          "frames. Returning 1e-5. Please check your wav files",
                          RuntimeWarning)
            return 1e-5

        # Apply OB matrix to the spectrograms as in Eq. (1)
        x_tob = np.sqrt(np.matmul(self._obm, np.square(np.abs(x_spec))))
        y_tob = np.sqrt(np.matmul(self._obm, np.square(np.abs(y_spec))))

        # For some values of fs, nfft, and min_freq the resulting obm has third-octave bands (in lower frequencies) that
        # do not include any frequency bins, so these bands will only hold zeros. To prevent an influence on the
        # mean correlation we remove the zero rows from further computation here.
        delete_zero_rows = np.logical_not(np.any(self._obm, axis=1))
        x_tob = np.delete(x_tob, delete_zero_rows, 0)
        y_tob = np.delete(y_tob, delete_zero_rows, 0)

        # Take segments of x_tob, y_tob
        x_segments = np.array(
            [x_tob[:, m - self._n_segmentation:m] for m in range(self._n_segmentation, x_tob.shape[1] + 1)])
        y_segments = np.array(
            [y_tob[:, m - self._n_segmentation:m] for m in range(self._n_segmentation, x_tob.shape[1] + 1)])

        # Find normalization constants and normalize
        normalization_consts = (
            np.linalg.norm(x_segments, axis=2, keepdims=True) /
            (np.linalg.norm(y_segments, axis=2, keepdims=True) + utils.EPS))
        y_segments_normalized = y_segments * normalization_consts

        # Clip as described in [1]
        clip_value = 10 ** (-self._beta / 20)
        y_primes = np.minimum(
            y_segments_normalized, x_segments * (1 + clip_value))

        # Subtract mean vectors
        y_primes = y_primes - np.mean(y_primes, axis=2, keepdims=True)
        x_segments = x_segments - np.mean(x_segments, axis=2, keepdims=True)

        # Get intermediate intelligibility in [1] eq. 5
        correlations_components = np.sum(y_primes * x_segments, axis=2) / (
                np.linalg.norm(y_primes, axis=2) * np.linalg.norm(x_segments, axis=2) + utils.EPS)

        if self._variation == "pre-mean":
            return correlations_components

        # Find the mean of all correlations as in [1], eq.6
        return np.mean(correlations_components)

    def export_config(self) -> dict:
        """
        Export the parameters as dictionary.
        :return: Dictionary containing parameters
        """
        out_config = dict(
            fs=int(self._fs),
            block_size=int(self._block_size),
            nfft=int(self._nfft),
            min_freq=int(self._min_freq),
            max_freq=int(self._max_freq),
            n_segmentation=int(self._n_segmentation),
            beta=float(self._beta),
            dyn_range=float(self._dyn_range),
            variation=str(self._variation))
        return out_config
