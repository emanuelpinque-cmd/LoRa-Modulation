import Chirp as Chirp
import numpy as np
import matplotlib.pyplot as plt
import SDR as SDR
from testerLab import VirtualTester


def test4():
    n = 100000
    SF = 4
    symbol = 2
    N = 2 ** SF
    snr_list = list(range(-30, -20))   # SNR in dB, linear axis
    ber_list = []
    for snr_db in snr_list:
        noise = np.sqrt(1 / (2 * N * 10 ** (snr_db / 10)))
        functions = Chirp.chirpFactory(n, SF, symbol, noise, 1.0)
        ber_list.append(VirtualTester(SF).getBER(functions,symbol))
    plt.plot(snr_list, ber_list)
    plt.xlabel("SNR (dB)")
    plt.ylabel("Error rate")
    plt.grid(True, which="both")
    plt.show()

def test5():
    n = 100
    SF = 4



    snr_list = np.arange(-1,0,0.01)
    ber_list = []
    for snr_db in snr_list:
        #snr_db = log_10(pseñal/pruido)
        #10**snr_db = pseñal/pruido
        noise = 1/(2**SF*10**snr_db)

        #pruido = snr*(1/2**SF)


        functions = Chirp.PreambleFactory(n,SF,noise)
        ber_list.append(VirtualTester(SF).getSER(functions))
    plt.semilogy(snr_list, ber_list)
    plt.xlabel("SNR (dB)")
    plt.ylabel("Error rate")
    plt.grid(True, which="both")
    plt.show()


if __name__ == "__main__":
    test5()