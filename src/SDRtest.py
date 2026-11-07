import adi
import numpy as np
import matplotlib.pyplot as plt

frec = int(2.4e9)
bw = int(10e6)

sdr = adi.Pluto(uri="ip:192.168.1.33")
sdr.rx_lo = frec
sdr.sample_rate = bw
sdr.rx_rf_bandwidth = bw
sdr.gain_control_mode_chan0 = "manual"
sdr.rx_hardwaregain_chan0 = 40
sdr.rx_buffer_size = 2**12

sdr.rx()
samples = sdr.rx()

omega = np.fft.fftshift(np.fft.fft(samples))
plt.plot(np.abs(omega))
plt.show()