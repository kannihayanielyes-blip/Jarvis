"""
listener.py — détection de double clap (callback + FFT + détection de transitoire).

Un clap est caractérisé par :
  1. Un pic d'amplitude bref : 1 à CLAP_MAX_BLOCKS blocs consécutifs au-dessus du seuil
  2. Une fréquence dominante dans [1000, 8000] Hz
  → Si le son dure plus de CLAP_MAX_BLOCKS blocs (~200ms) : c'est une voix ou un bruit continu, ignoré.

Machine d'état par bloc :
  IDLE       → pic détecté          → BURSTING (debut du transitoire)
  BURSTING   → bloc encore élevé    → incrément burst_count
             → burst_count > max    → SUPPRESSED (son trop long, pas un clap)
             → pic retombe          → évalue : clap valide si 1 ≤ burst_count ≤ max ET freq OK
  SUPPRESSED → bloc retombe         → IDLE (reset sans déclencher)
"""

import time
import threading
import numpy as np
import sounddevice as sd
import config


SAMPLE_RATE = 44100
BLOCK_DURATION = 0.05        # 50ms par bloc → 1 bloc = 50ms

CLAP_AMP_THRESHOLD = 0.03    # amplitude minimum pour entrer en burst
CLAP_FREQ_MIN = 1000         # Hz — borne basse fréquence clap
CLAP_FREQ_MAX = 8000         # Hz — borne haute fréquence clap
CLAP_MAX_BLOCKS = 4          # max 4 blocs (~200ms) — au-delà c'est un son continu

DOUBLE_CLAP_MIN = 0.3        # intervalle min entre deux claps (secondes)
DOUBLE_CLAP_MAX = 1.5        # intervalle max (reset si dépassé)
COOLDOWN = 0.2               # ignore les pics dans les 200ms suivant un clap validé


def wait_for_clap():
    """Bloque jusqu'à détecter un double clap."""
    block_size = int(SAMPLE_RATE * BLOCK_DURATION)

    state = {
        "phase": "IDLE",         # IDLE | BURSTING | SUPPRESSED
        "burst_count": 0,
        "burst_peak": 0.0,
        "burst_freq": 0.0,
        "first_clap_time": None,
        "last_clap_time": None,
    }
    triggered = threading.Event()

    def _dominant_freq(block: np.ndarray) -> float:
        flat = block.flatten()
        spectrum = np.abs(np.fft.rfft(flat))
        freqs = np.fft.rfftfreq(len(flat), d=1.0 / SAMPLE_RATE)
        return float(freqs[np.argmax(spectrum)])

    def _register_clap(peak: float, freq: float):
        """Appelé quand un transitoire bref et fréquentiellement valide se termine."""
        now = time.monotonic()

        # Cooldown après un clap précédent
        if state["last_clap_time"] is not None:
            if (now - state["last_clap_time"]) < COOLDOWN:
                return

        if not (CLAP_FREQ_MIN <= freq <= CLAP_FREQ_MAX):
            print(f"[debug] transitoire ignoré : freq={freq:.0f}Hz hors zone")
            return

        state["last_clap_time"] = now
        print(f"[clap détecté!] peak={peak:.3f} freq={freq:.0f}Hz")

        if state["first_clap_time"] is None:
            state["first_clap_time"] = now
        else:
            interval = now - state["first_clap_time"]
            if interval > DOUBLE_CLAP_MAX:
                print(f"[listener] Intervalle trop long ({interval:.2f}s), reset.")
                state["first_clap_time"] = now
            elif interval >= DOUBLE_CLAP_MIN:
                print(f"[listener] Double clap validé ! (intervalle={interval:.2f}s)")
                triggered.set()
            # interval < DOUBLE_CLAP_MIN → trop rapide (bruit/écho), ignoré

    def callback(indata, frames, time_info, status):
        peak = float(np.max(np.abs(indata)))
        freq = _dominant_freq(indata)

        phase = state["phase"]

        if phase == "IDLE":
            if peak >= CLAP_AMP_THRESHOLD:
                # Début d'un transitoire
                state["phase"] = "BURSTING"
                state["burst_count"] = 1
                state["burst_peak"] = peak
                state["burst_freq"] = freq
                print(f"[debug] burst start — peak={peak:.3f} freq={freq:.0f}Hz")
            else:
                # Silence : expire le premier clap si trop vieux
                if state["first_clap_time"] is not None:
                    if (time.monotonic() - state["first_clap_time"]) > DOUBLE_CLAP_MAX:
                        print("[listener] Timeout premier clap, reset.")
                        state["first_clap_time"] = None

        elif phase == "BURSTING":
            if peak >= CLAP_AMP_THRESHOLD:
                state["burst_count"] += 1
                # Garde le pic max et la fréquence du bloc le plus fort
                if peak > state["burst_peak"]:
                    state["burst_peak"] = peak
                    state["burst_freq"] = freq
                print(f"[debug] burst bloc {state['burst_count']} — peak={peak:.3f} freq={freq:.0f}Hz")

                if state["burst_count"] > CLAP_MAX_BLOCKS:
                    # Son trop long → pas un clap
                    print(f"[debug] son continu détecté ({state['burst_count']} blocs), supprimé.")
                    state["phase"] = "SUPPRESSED"
            else:
                # Pic retombé → transitoire terminé, évalue
                blocs = state["burst_count"]
                p = state["burst_peak"]
                f = state["burst_freq"]
                print(f"[debug] burst terminé — {blocs} bloc(s), peak={p:.3f} freq={f:.0f}Hz")
                state["phase"] = "IDLE"
                state["burst_count"] = 0
                _register_clap(p, f)

        elif phase == "SUPPRESSED":
            if peak < CLAP_AMP_THRESHOLD:
                # Son continu terminé, retour en veille
                state["phase"] = "IDLE"
                state["burst_count"] = 0

    print(
        f"[listener] En attente d'un double clap "
        f"(amp>={CLAP_AMP_THRESHOLD}, freq={CLAP_FREQ_MIN}-{CLAP_FREQ_MAX}Hz, "
        f"max {CLAP_MAX_BLOCKS} blocs)"
    )

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=block_size,
        callback=callback,
    ):
        triggered.wait()
