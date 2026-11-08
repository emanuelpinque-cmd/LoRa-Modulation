import numpy as np
import matplotlib.pyplot as plt
import Chirp
import SDR
class VirtualTester:
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

    def graphBer(self):
        N = 2 ** self.SF
        n = len(self.functions)
        snr_list = list(range(-30, -10))  # SNR in dB, linear axis
        ber_list = []
        for snr_db in snr_list:
            noise = np.sqrt(1 / (2 * N * 10 ** (snr_db / 10)))
            functions = Chirp.chirpFactory(n, self.SF, self.sent, noise, 1.0)
            ber_list.append(VirtualTester(functions, self.sent, self.SF).getBER())
        plt.semilogy(snr_list, ber_list)  # Y log, X lineal (dB)
        plt.xlabel("SNR (dB)")
        plt.ylabel("BER")
        plt.grid(True, which="both")
        plt.show()

    def graphSER(self, threshold=0.25):
        N = 2 ** self.SF
        n = len(self.functions)
        snr_list = list(range(-30, 6))
        ser_list = []
        for snr_db in snr_list:
            noise = np.sqrt(1 / (2 * N * 10 ** (snr_db / 10)))
            functions = [Chirp.makeChirpPreamble(self.SF, noise) for _ in range(n)]
            ser_list.append(VirtualTester(functions, self.sent, self.SF).getSER(threshold))
        plt.semilogy(snr_list, ser_list)
        plt.xlabel("SNR (dB)")
        plt.ylabel("SER (preamble detection)")
        plt.grid(True, which="both")
        plt.show()

    def getSER(self,threshold=0.8):
        p = Chirp.makeChirpPreamble(self.SF,0.0)
        errors = 0
        for f in self.functions:
            (correct,delay) = f.getPreambleEnergy(p,threshold)
            if not correct:
                errors += 1
        return errors / len(self.functions)