import  adi
import numpy as np

import Chirp
from SDR import SamplesAndTime

SCALE = 2**14  # Pluto expects 16-bit samples (range +-2^14)


class Pluto:
    def __init__(self, sdr, bw, lo, SF):
        self.sdr = sdr
        self.uri = sdr.uri      # ip comes from the sdr object
        self.bw = bw
        self.lo = lo
        self.SF = SF
        self.sdr.sample_rate = bw


class PlutoTx(Pluto):
    def __init__(self, sdr, bw, gain, SF, lo):
        super().__init__(sdr, bw, lo, SF)
        self.gain = gain                      # range: -89.75 to 0 dB
        self.sdr.tx_lo = lo
        self.sdr.tx_rf_bandwidth = bw
        self.sdr.tx_hardwaregain_chan0 = gain

    def send(self, samples, cyclic=True):
        # WARNING: with cyclic=True the buffer transmits forever.
        # Call stop() when done, otherwise the Pluto keeps emitting.
        self.sdr.tx_cyclic_buffer = cyclic    # must be set before tx()
        self.sdr.tx(np.asarray(samples) * SCALE)

    def sendChirp(self, symbols, up=1.0, noise=0.0, startDelay=0, endDelay=0):
        # Build a chirp sequence at this SF and transmit it (same cyclic warning)
        data = Chirp.chirpSeq(self.SF, symbols, noise, up, startDelay, endDelay)
        self.send(data.samples)
        return data

    def sendPreamble(self, noise=0.0):
        # Transmit the default preamble at this SF (same cyclic warning)
        data = Chirp.makeChirpPreamble(self.SF, noise)
        self.send(data.samples)
        return data

    def stop(self):
        # Stop the cyclic transmission
        self.sdr.tx_destroy_buffer()


class PlutoRx(Pluto):
    def __init__(self, sdr, bw, gain, SF, lo, buffer_size=2**11):
        super().__init__(sdr, bw, lo, SF)
        self.gain = gain                      # range: 0 to 73 dB
        self.buffer_size = buffer_size
        self.sdr.rx_lo = lo
        self.sdr.rx_rf_bandwidth = bw
        self.sdr.gain_control_mode_chan0 = "manual"
        self.sdr.rx_hardwaregain_chan0 = gain
        self.sdr.rx_buffer_size = buffer_size

    def receive(self):
        self.sdr.rx()                         # discard first buffer
        return self.sdr.rx()

    def listen(self, preamble=None, threshold_ratio=0.8):
        # Default preamble for this SF
        if preamble is None:
            preamble = Chirp.makeChirpPreamble(self.SF, 0.0)

        self.sdr.rx()  # discard first buffer

        # Block until the preamble shows up
        while True:
            rx_samples = self.sdr.rx()
            time = np.arange(len(rx_samples))
            st = SamplesAndTime(time, rx_samples)
            found, lag = st.getPreamble(preamble, threshold_ratio)
            if found:
                return rx_samples, lag

    def stop(self):
        self.sdr.rx_destroy_buffer()

if __name__ == "__main__":
        SF = 5
        frec = int(2.4e9)
        bw = int(1e6)
        tx_gain = -30
        rx_gain = 40

        # One Pluto shared by TX and RX (loopback)
        dev = adi.Pluto(uri="ip:192.168.1.34")
        tx = PlutoTx(dev, bw, tx_gain, SF, frec)
        rx = PlutoRx(dev, bw, rx_gain, SF, frec, buffer_size=2 ** 11)

        try:
            # Transmitter: preamble repeats until stop()
            tx.sendPreamble()

            # Receiver: blocks until the preamble is detected
            rx_samples, lag = rx.listen()
            print(f"Preamble found at sample {lag}")
        finally:
            # Always stop the cyclic transmission
            tx.stop()
            rx.stop()

        # Plot what was received
        st = SamplesAndTime(np.arange(len(rx_samples)), rx_samples)
        st.graphSpectrogram(nfft=16, title="Received preamble")
        st.graphFrequencyChirp(title="Instantaneous frequency")