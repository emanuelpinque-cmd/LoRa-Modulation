import SDR as SDR
import numpy as np
import matplotlib as plt

### Make an array of chirp (same simbol)

#def chirpSeq(N,SF,symbols,noise,up):



def chirpFactory(N, SF, symbol, noise, up):
    functions = []
    for _ in range(N):
        functions.append(makeFastChirp(SF, symbol, noise, up))
    return functions


def makeFastChirp(SF, symbol, noise, up):
    a = ChirpFunction(SF, symbol, up)
    b = NoisyChirp(a, noise)
    return SDR.SamplesAndTime(b.time, b.getSamples())

class ChirpFunction:
    resolution = 1
    def __init__(self,SF:int,symbol:int,up):
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

class NoisyChirp:
        def __init__(self, chirpFunction, noise):
            self.chirpFunction = chirpFunction
            self.time = chirpFunction.k.copy()
            n = len(chirpFunction.f)
            ruido = noise * (np.random.randn(n) + 1j * np.random.randn(n))
            self.samples = chirpFunction.f + ruido
            self.resolution = chirpFunction.resolution

        def getTime(self): return self.time

        def getSamples(self): return self.samples

