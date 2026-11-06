import adi
import numpy as np
from Chirp import makeFastChirp
import SDR
sdr = adi.Pluto(uri="ip:192.168.1.32")
print(sdr)