import adi
import numpy as np

import Chirp
import SDR
from PlutoSDR import PlutoTx, PlutoRx


class RealTester:
    def __init__(self, SF=8, frec=int(2.4e9), bw=int(1e6), uri="ip:192.168.1.35"):
        self.SF = SF
        self.frec = frec
        self.bw = bw
        self.uri = uri

    # ---------- helpers (lo que antes vivía en PlutoTx / PlutoRx) ----------
    def _sendChirp(self, tx, symbols, up=1.0, noise=0.0, startDelay=0, endDelay=0):
        data = Chirp.chirpSeq(self.SF, symbols, noise, up, startDelay, endDelay)
        tx.sendCyclic(data.samples)
        return data

    def _sendPreamble(self, tx, noise=0.0):
        data = Chirp.makeChirpPreamble(self.SF, noise)
        data.graphSpectrogram(title="Theorical")
        tx.sendCyclic(data.samples)
        return data

    def _preambleDetector(self, threshold_ratio, preamble=None):
        if preamble is None:
            preamble = Chirp.makeChirpPreamble(self.SF, 0.0)

        def detector(rx_samples):
            time = np.arange(len(rx_samples))
            st = SDR.SamplesAndTime(time, rx_samples)
            return st.getPreambleEnergy(preamble, threshold_ratio)

        return detector

    # ---------- tests ----------
    def preambleTest(self, tx_gain=-10, rx_gain=40, threshold_ratio=0.95,
                     buffer_size=2 ** 15, window=3000):
        # One Pluto shared by TX and RX (loopback)
        dev = adi.Pluto(uri=self.uri)
        tx = PlutoTx(dev, self.bw, tx_gain, self.SF, self.frec)
        rx = PlutoRx(dev, self.bw, rx_gain, self.SF, self.frec, buffer_size=buffer_size)

        try:
            # Transmitter: preamble repeats until stop()
            self._sendPreamble(tx)

            # Receiver: blocks until the preamble is detected
            rx_samples, lag = rx.listen(self._preambleDetector(threshold_ratio))
            samples = SDR.SamplesAndTime(np.arange(window), rx_samples[:window])
            samples.graphSpectrogram(nfft=16, title="Received preamble")
            print(f"Preamble found at sample {lag}")
        finally:
            # Always stop the cyclic transmission
            tx.stop()
            rx.stop()

        # Plot what was received
        st = SDR.SamplesAndTime(np.arange(len(rx_samples)), rx_samples)
        st.graphSpectrogram(nfft=16, title="Received preamble")
        st.graphFrequencyChirp(title="Instantaneous frequency")

    def graphChirp(self, tx_gain=0, rx_gain=40, buffer_size=2 ** 13, window=2800):
        dev = adi.Pluto(uri=self.uri)
        rx = PlutoRx(dev, self.bw, rx_gain, self.SF, self.frec, buffer_size=buffer_size)
        tx = PlutoTx(dev, self.bw, tx_gain, self.SF, self.frec)
        # transmit
        self._sendPreamble(tx)
        # receive
        rx.sdr.rx()
        samples = rx.sdr.rx()
        SaT = SDR.SamplesAndTime(np.arange(window), samples[:window])
        SaT.graphSpectrogram(nfft=128, title="Received preamble")


if __name__ == "__main__":
    RealTester().preambleTest(tx_gain=-65,threshold_ratio=0.6)
