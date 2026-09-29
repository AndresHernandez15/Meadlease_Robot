import argparse
import numpy as np
from scipy.io import wavfile

C, D = 343.0, 0.22          # velocidad del sonido, separación mics extremos (ajústala)
PAIR = (0, 3)               # canales 1 y 4
FS_UP = 16                  # factor de interpolación

def gcc_phat(a, b, fs, max_tau, up):
    n = len(a) + len(b)
    A, B = np.fft.rfft(a, n), np.fft.rfft(b, n)
    R = A * np.conj(B)
    R /= np.abs(R) + 1e-12
    cc = np.fft.irfft(R, n * up)
    m = int(fs * up * max_tau)
    cc = np.concatenate((cc[-m:], cc[:m + 1]))
    return (np.argmax(np.abs(cc)) - m) / (fs * up)

parser = argparse.ArgumentParser(description="Estima el ángulo de llegada del audio de un array Kinect.")
parser.add_argument("wav", help="archivo WAV de entrada")
args = parser.parse_args()

fs, x = wavfile.read(args.wav)
x = x.astype(np.float64) / 2**31
win = fs // 4
for i in range(0, len(x) - win, win):
    f = x[i:i + win]
    if np.sqrt(np.mean(f**2)) < 0.004:      # descarta silencio
        continue
    tau = gcc_phat(f[:, PAIR[0]], f[:, PAIR[1]], fs, D / C, FS_UP)
    ang = np.degrees(np.arcsin(np.clip(tau * C / D, -1, 1)))
    print(f"t={i/fs:4.2f}s  tau={tau*1e6:7.1f} µs  ángulo≈{ang:6.1f}°")