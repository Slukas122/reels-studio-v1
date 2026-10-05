#!/usr/bin/env python3
"""Zmeria tempo a beaty skladby (len numpy + ffmpeg, bez librosa).
   python3 beats.py hudba.mp3 [--from 12.5] [--dur 15]  → vypíše JSON a uloží beats.json
   V filme potom:  const B = M.beats(bpm, offset)  a render:  node render.mjs film.html --track hudba.mp3 --track-from 12.5
"""
import sys, json, subprocess, shutil, numpy as np

def ffmpeg():
    if shutil.which('ffmpeg'): return 'ffmpeg'
    import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()

args = sys.argv[1:]; path = args[0]
opt = lambda k, d: float(args[args.index(k) + 1]) if k in args else d
start, dur, SR, HOP = opt('--from', 0), opt('--dur', 0), 22050, 512
cmd = [ffmpeg(), '-v', 'error', '-ss', str(start), '-i', path] + (['-t', str(dur)] if dur else []) + ['-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
y = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32)
if len(y) < SR * 2: sys.exit('Skladba je príliš krátka.')
# onset envelope = spektrálny tok
N = 2048; win = np.hanning(N); frames = 1 + (len(y) - N) // HOP
S = np.abs(np.fft.rfft(np.stack([y[i*HOP:i*HOP+N] * win for i in range(frames)]), axis=1))
S = np.log1p(100 * S); D = np.maximum(0, np.diff(S, axis=0)); flux = np.concatenate([[0], D.sum(axis=1)])
low = np.concatenate([[0], D[:, 2:16].sum(axis=1)])  # ~20–170 Hz (kick) na fázu
flux = np.convolve(flux - flux.mean(), np.ones(3) / 3, 'same'); flux = np.maximum(flux, 0)
fps = SR / HOP
# tempo: autokorelácia, preferencia okolo 115 BPM
ac = np.correlate(flux, flux, 'full')[len(flux)-1:]
best, bpm = -1, 120
def acv(lag):
    l0 = int(lag); fr = lag - l0
    return 0 if l0 + 1 >= len(ac) else ac[l0] * (1 - fr) + ac[l0 + 1] * fr
for b in np.arange(70, 181, 0.1):
    lag = fps * 60 / b
    v = sum(acv(lag * m) / m ** 0.5 for m in (1, 2, 4)) * np.exp(-0.5 * (np.log2(b / 115) / 0.9) ** 2)
    if v > best: best, bpm = v, b
period = fps * 60 / bpm
# fáza: posun s najväčšou sumou onsetov na mriežke
phases = np.arange(0, period, 0.25)
lowc = np.convolve(low, np.ones(3) / 3, 'same')
score = [lowc[np.clip(np.round(p + np.arange(0, len(flux) - p, period)).astype(int), 0, len(flux)-1)].sum() for p in phases]
off = phases[int(np.argmax(score))] / fps + (N / 2 - HOP) / SR
off = off % (60 / bpm)
beats = [round(off + k * 60 / bpm, 3) for k in range(int((len(y) / SR - off) / (60 / bpm)) + 1)]
# downbeat: z 4 možných fáz tá s najsilnejšími onsetmi
bi = [int(round(b * fps)) for b in beats]
dsc = [sum(lowc[min(i, len(flux)-1)] for i in bi[k::4]) for k in range(4)]
d0 = int(np.argmax(dsc))
out = {'bpm': round(float(bpm), 2), 'offset': beats[d0], 'beats': beats, 'downbeats': beats[d0::4], 'from': start, 'duration': round(len(y) / SR, 2)}
json.dump(out, open('beats.json', 'w'), indent=1)
print(json.dumps({k: out[k] for k in ['bpm', 'offset', 'from', 'duration']}, ensure_ascii=False))
print(f"→ vo filme: const B = M.beats({out['bpm']}, {out['offset']});  music: {{ style: 'none' }}")
print(f"→ render:   node render.mjs film.html --track {path} --track-from {start}")
