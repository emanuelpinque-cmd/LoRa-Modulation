import Chirp as Chirp
import SDR as SDR
import numpy as np
import matplotlib.pyplot as plt
import testerLab as Tester
def test1():
    n = 1000
    SF = 4
    symbol = 2
    noise = 0.0
    up = 1.0
    Functions = Chirp.chirpFactory(n, SF, symbol, noise, up)
    BER = SDR.Tester(Functions,symbol,SDR).getBER()
    print(BER)
    Functions[0].graphFrequency()
def test2():
    for s in range(2 ** 4):
        c = Chirp.ChirpFunction(4, s, 1.0)
        x = SDR.SamplesAndTime(c.k, c.f)
        assert x.estimateSymbol() == s, s
    print("OK")
def test3():
    snr_db = -100
    n = 100000
    SF = 4
    symbol = 2
    noise = np.sqrt(1 / (2 * 2 ** SF * 10 ** (snr_db / 10)))
    functions = Chirp.chirpFactory(n, SF, symbol, noise, 1.0)
    print(SDR.Tester(functions, symbol, SF).getBER())


if __name__ == "__main__":
    SF = 8
    M = 2 ** SF
    symbols = Chirp.makeChirpPreamble(SF, 0.01)
    symbols.graphSpectrogram(nfft=32, title="Simulated chirps")

