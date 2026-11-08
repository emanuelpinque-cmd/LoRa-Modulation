import adi
import numpy as np
import matplotlib.pyplot as plt

import Chirp
from SDR import SamplesAndTime

### Chirp
SF = 5
### Parametters
frec = int(2.4e9)
bw = int(1e6)
tx_gain = -30
rx_gain = 40
bufferSize = int(2**8)   # 256 muestras = 2 repeticiones del buffer TX (128)
sdr = adi.Pluto(uri="ip:192.168.1.34")
sdr.rx_lo = frec
sdr.tx_lo = frec
sdr.sample_rate = bw
sdr.rx_rf_bandwidth = bw
sdr.tx_rf_bandwidth = bw
sdr.gain_control_mode_chan0 = "manual"
sdr.rx_hardwaregain_chan0 = rx_gain
sdr.tx_hardwaregain_chan0 = tx_gain
sdr.rx_buffer_size = bufferSize


_tx_original = sdr.tx
sdr.tx = lambda x: _tx_original(np.asarray(x) * 2**14)

def send():
    ## trasmit
    sdr.tx_cyclic_buffer = True
    ## make the chirp
    data = Chirp.chirpSeq(SF,[0,22,41,21],0.0,1.0,0,0)
    samples = data.samples
    sdr.tx(samples)
    data.graphFrequencyChirp()
def recive():
    ###recive
    sdr.rx()
    rx_samples = sdr.rx()
    time = np.arange(len(rx_samples))
    st = SamplesAndTime(time,rx_samples)
    st.graphFrequencyChirp()
def stop():
    sdr.tx_destroy_buffer()
    sdr.rx_destroy_buffer()
def test_chirp(ip="192.168.1.34", sf=5, freq=int(2.4e9), bw=int(10e6),tx_gain=-30, rx_gain=30, buffer_size=2**8, nfft=8, hop=8):
    sdr = adi.Pluto(uri=f"ip:{ip}")
    sdr.rx_lo = freq
    sdr.tx_lo = freq
    sdr.sample_rate = bw
    sdr.rx_rf_bandwidth = bw
    sdr.tx_rf_bandwidth = bw
    sdr.gain_control_mode_chan0 = "manual"
    sdr.rx_hardwaregain_chan0 = rx_gain    # RX range: 0 to 73 dB
    sdr.tx_hardwaregain_chan0 = tx_gain    # TX range: -89.75 to 0 dB
    sdr.rx_buffer_size = buffer_size

    samples = Chirp.chirpSeq(sf, [0, 0, 0, 0], 0.0, 1.0, 0, 0).samples

    try:
        sdr.tx_cyclic_buffer = True
        sdr.tx(samples * 2**14)
        sdr.rx()                      # discard first buffer
        rx_samples = sdr.rx()
    finally:
        sdr.tx_destroy_buffer()       # always stop the cyclic transmission
        sdr.rx_destroy_buffer()
        del sdr

    window = np.hanning(nfft)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, x, title in zip(axes, (samples, rx_samples), ("Generated", "Received")):
        x = np.asarray(x)
        n_frames = (len(x) - nfft) // hop + 1
        S = np.array([np.abs(np.fft.fftshift(np.fft.fft(x[i*hop : i*hop + nfft] * window)))
                      for i in range(n_frames)]).T
        im = ax.imshow(20 * np.log10(S + 1e-9), aspect="auto", origin="lower",
                       extent=[0, len(x) / bw * 1e6, -bw / 2e6, bw / 2e6])
        ax.set_title(title)
        ax.set_xlabel("Time (us)")
        ax.set_ylabel("Frequency (MHz)")
        fig.colorbar(im, ax=ax, label="dB")
    plt.show()
#stop()
send()
recive()
