from json.decoder import NaN

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import false_discovery_control

import SDR as SDR
import Chirp as CP


class  SamplesAndTime:
    def __init__(self,time,samples):
        #init time & samples
        self.time = time
        self.samples = samples
        #N the number of samples on a chirp is the SF
        self.N = len(samples)
        self.chirpDown()
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




    def getPreamble(self,preamble,preamblelen):
        iscorrect = False
        displacement = NaN
        p = np.asarray(getattr(preamble, "samples", preamble))
        c = np.correlate(self.samples, p, mode="full")

        dt = self.time[1] - self.time[0]
        lags = np.arange(-(len(p) - 1), len(self.samples)) * dt

        amp = np.max(c)
        if amp +0.1 > preamblelen:
            displacement = np.argmax(lags)
            idx = np.argmax(c)
            displacement = lags[idx]
            iscorrect = True
        return iscorrect, displacement


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
class Tester:
    def __init__(self, functions, sent_symbol, SF):
            self.functions = functions
            self.sent = sent_symbol
            self.SF = SF

    def getBER(self):
        errors = 0
        for f in self.functions:
            f.chirpDown()
            if not f.isSymbolCorrect(self.sent):
                errors += 1
        return errors / len(self.functions)
