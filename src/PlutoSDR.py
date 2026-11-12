import numpy as np

SCALE = 2**13 * np.sqrt(2**8)


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

    def sendCyclic(self, samples):
        # Workaround: the Pluto only repeats the first quarter of the buffer
        self.send(np.tile(samples, 4))

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

    def listen(self, detector):
        # detector(rx_samples) -> (found, lag). The Pluto doesn't know
        # what is being detected; whoever calls decides.
        self.sdr.rx()  # discard first buffer

        # Block until the detector fires

        while True:
            rx_samples = self.sdr.rx()
            found, lag = detector(rx_samples)
            print("listing preamble...")
            if found:
                return rx_samples, lag

    def stop(self):
        self.sdr.rx_destroy_buffer()