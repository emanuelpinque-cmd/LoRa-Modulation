import Chirp as Chirp
import SDR as SDR
import numpy as np
import matplotlib.pyplot as plt
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
def test4():
    n = 1000
    SF = 4
    symbol = 2
    N = 2 ** SF
    snr_list = list(range(-20, 1))   # SNR in dB, linear axis
    ber_list = []
    for snr_db in snr_list:
        noise = np.sqrt(1 / (2 * N * 10 ** (snr_db / 10)))
        functions = Chirp.chirpFactory(n, SF, symbol, noise, 1.0)
        ber_list.append(SDR.Tester(functions, symbol, SF).getBER())
    plt.plot(snr_list, ber_list)
    plt.xlabel("SNR (dB)")
    plt.ylabel("Error rate")
    plt.grid(True, which="both")
    plt.show()

seq = Chirp.chirpSeq(4, [10], 0.0, 1.0,2,2)
seq.graphFrequency()