import numpy as np
import matplotlib.pyplot as plt
class ChirpFunction:
    resolution = 1
    def __init__(self,SF,symbol,up):
        self.SF = SF
        self.up = up
        self.symbol = symbol
        (self.k,self.f) = self.makeF()

    def graphReal(self):
        plt.plot(self.k,self.f.real)
        plt.show()
    def graphPhase(self):
        plt.plot(self.k, self.phase)
        plt.show()
    def graphFrec(self):
        plt.plot(self.k, self.frec)
        plt.show()
    def makeF(self):
            N = 2 ** self.SF
            t = np.arange(N * self.resolution) / self.resolution
            phase = 2 * np.pi * ((self.symbol + t) % N) * t / N
            f = np.exp(1j * self.up * phase) / np.sqrt(N)
            return t, f