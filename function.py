import numpy as np
import matplotlib.pyplot as plt

def chirpFactory(N, SF, symbol, noise, up):
    functions = []
    for _ in range(N):
        a = ChirpFunction(SF, symbol, up)
        b = NoisyChirp(a, noise)
        functions.append(SamplesAndTime(b.time, b.getSamples()))
    return functions

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

class NoisyChirp:
    def __init__(self, chirpFunction, noise):
        self.chirpFunction = chirpFunction
        self.time = chirpFunction.k.copy()
        n = len(chirpFunction.f)
        ruido = noise * (np.random.randn(n) + 1j*np.random.randn(n))
        self.samples = chirpFunction.f + ruido
        self.resolution = chirpFunction.resolution
    def getTime(self): return self.time
    def getSamples(self): return self.samples

class  SamplesAndTime:
    def __init__(self,time,samples):
        self.time = time
        self.samples = samples
        self.N = len(samples)
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
        plt.plot(self.time, abs(self.fft))
        plt.show()
    def estimateSymbol(self):
        return np.argmax(np.abs(self.fft))
    def isSymbolCorrect(self,symbol):
        return symbol == self.estimateSymbol()

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

chirps = chirpFactory(1000,4,2,1.0,1.0)
Tester = Tester(chirps,2,4)
print(Tester.getBER())