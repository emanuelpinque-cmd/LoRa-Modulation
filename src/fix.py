import adi
sdr = adi.Pluto(uri="ip:192.168.1.35")
sdr.sample_rate = int(2.5e6)
sdr.rx_lo = int(2.4e9)
sdr.rx_rf_bandwidth = int(2e6)
sdr.gain_control_mode_chan0 = "manual"
sdr.rx_hardwaregain_chan0 = 40
sdr.rx_buffer_size = 2**12
print(sdr.sample_rate)
x = sdr.rx()
print(len(x), x[:5])