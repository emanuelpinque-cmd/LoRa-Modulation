from json.decoder import NaN

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import false_discovery_control




class  SamplesAndTime:
    def __init__(self,time,samples):
        #init time & samples
        self.time = time
        self.samples = samples
        #N the number of samples on a chirp is the SF
        self.N = len(samples)
        self.chirpDown()

    def graphSpectrogram(self, fs=None, nfft=32, ax=None, title=None):
        # Simple spectrogram: time on x, frequency on y, color is power (dB)
        show = ax is None
        if ax is None:
            ax = plt.gca()

        x = np.asarray(self.samples)
        nfft = min(nfft, len(x))
        # fs=None -> normalized frequency (cycles/sample)
        ax.specgram(x, NFFT=nfft, Fs=fs if fs else 1.0,
                    noverlap=nfft * 3 // 4, cmap="viridis")

        ax.set_xlabel("Time (s)" if fs else "Time (samples)")
        ax.set_ylabel("Frequency (Hz)" if fs else "Frequency (cycles/sample)")
        if title:
            ax.set_title(title)
        if show:
            plt.show()


    def trunk(self, trunk):
        n = len(self.time) - trunk
        self.time = self.time[:n]
        self.samples = self.samples[:n]
        self.N = n
        self.chirpDown()

    def graphFrequencyChirp(self, fs=None, ax=None, title=None):
        z = self.samples[1:] * np.conj(self.samples[:-1])
        dt = np.diff(self.time)
        frequency = np.angle(z) / (2 * np.pi * dt)
        frequency[np.abs(z) == 0] = 0
        time_mid = self.time[:-1] + dt / 2

        if fs is not None:
            frequency = frequency * fs / 1e6  # MHz
            time_mid = time_mid / fs * 1e6  # us
            xlabel, ylabel = "Time (us)", "Frequency (MHz)"
        else:
            xlabel, ylabel = "Time", "Frequency"

        show = ax is None
        if ax is None:
            ax = plt.gca()
        ax.plot(time_mid, frequency, ".-", markersize=3)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True)
        if title:
            ax.set_title(title)
        if show:
            plt.show()

    def SamplesAndTime(self):
        plt.plot(self.time, self.samples.real)
        plt.show()
    def graphReal(self):
        plt.plot(self.time, self.samples.real)
        plt.show()
    def chirpDown(self):
        d = self.samples * np.exp(-2j * np.pi * (self.time ** 2) / self.N)
        self.fft = np.fft.fft(d) / np.sqrt(self.N)
    def graphFFT(self):
        plt.plot(self.time, abs((self.fft)))
        plt.show()
    def estimateSymbol(self):
        return np.argmax(np.abs(self.fft))
    def isSymbolCorrect(self,symbol):
        return symbol == self.estimateSymbol()

    def graphFrequency(self):
        z = self.samples[1:] * np.conj(self.samples[:-1])
        dt = np.diff(self.time)
        frequency = np.angle(z) / (2 * np.pi * dt)
        frequency[np.abs(z) == 0] = 0   # silence drawn as a flat line at 0
        time_mid = self.time[:-1] + dt / 2
        plt.plot(time_mid, frequency)
        plt.xlabel("Time")
        plt.ylabel("Frequency")
        plt.grid(True)
        plt.show()
    def displaceTime(self,displacement):
        self.k = self.k+displacement

    def getPreamble(self, preamble, threshold_ratio=0.8):
        p = np.asarray(getattr(preamble, "samples", preamble))
        c = np.abs(np.correlate(self.samples, p, mode="full"))

        dt = self.time[1] - self.time[0]
        lags = np.arange(-(len(p) - 1), len(self.samples)) * dt

        threshold = threshold_ratio * np.sum(np.abs(p) ** 2)
        idx = np.argmax(c)
        if c[idx] > threshold:
            return True, lags[idx]
        return False, np.nan

    def getPreambleEnergy(self, preamble, threshold_ratio=0.8):
        p = np.asarray(getattr(preamble, "samples", preamble))
        x = self.samples


        c = np.abs(np.correlate(x, p, mode="valid"))


        win_energy = np.convolve(np.abs(x) ** 2, np.ones(len(p)), mode="valid")
        norm = np.sqrt(win_energy * np.sum(np.abs(p) ** 2))
        c = c / np.where(norm == 0, np.inf, norm)

        dt = self.time[1] - self.time[0]
        idx = np.argmax(c)
        if c[idx] > threshold_ratio:
            return True, idx * dt
        return False, np.nan


    def graphCorrelationPreamble(self, preamble):
        p = np.asarray(getattr(preamble, "samples", preamble))
        c = np.correlate(self.samples, p, mode="full")

        dt = self.time[1] - self.time[0]
        lags = np.arange(-(len(p) - 1), len(self.samples)) * dt

        idx = np.argmax(np.abs(c))
        print(f"Máximo: {np.abs(c)[idx]:.2f} en desfase {lags[idx]:.2f}")

        plt.plot(lags, np.abs(c))
        plt.xlabel("desfase")
        plt.ylabel("|correlación|")
        plt.grid(True)
        plt.show()
        return lags, c
