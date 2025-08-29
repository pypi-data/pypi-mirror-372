# music_engine/theory.py

import numpy as np
# We need our synthesis functions to render the note
from .synthesis import generate_wave, apply_adsr_envelope

# A dictionary to map note names to MIDI numbers for convenience
NOTE_TO_MIDI = {
    'C4': 60, 'C#4': 61, 'D4': 62, 'D#4': 63, 'E4': 64, 'F4': 65, 'F#4': 66, 'G4': 67, 'G#4': 68, 'A4': 69, 'A#4': 70, 'B4': 71,
    'C5': 72, 'C#5': 73, 'D5': 74, 'D#5': 75, 'E5': 76, 'F5': 77, 'F#5': 78, 'G5': 79, 'G#5': 80, 'A5': 81, 'A#5': 82, 'B5': 83,
    'C6': 84
}

class Note:
    def __init__(self, pitch, duration, amplitude=0.5):
        
        if isinstance(pitch, str):
            self.pitch = NOTE_TO_MIDI.get(pitch.upper())
            if self.pitch is None:
                raise ValueError(f"Unknown note name: {pitch}")
        else:
            self.pitch = pitch # MIDI number
        
        self.duration = duration # in beats
        self.amplitude = amplitude

    def _midi_to_freq(self):
        
        return 440 * (2 ** ((self.pitch - 69) / 12))

    def render(self, tempo, sample_rate=44100, waveform='sine', adsr_params=None):
        
        # Calculate duration in seconds from beats and tempo
        duration_sec = (60 / tempo) * self.duration
        
        # Get the note's frequency
        frequency = self._midi_to_freq()
        
        # Generate the raw wave
        wave = generate_wave(
            waveform=waveform,
            frequency=frequency,
            duration=duration_sec,
            sample_rate=sample_rate,
            amplitude=self.amplitude
        )
        
        # Apply ADSR envelope if provided
        if adsr_params:
            wave = apply_adsr_envelope(wave, duration_sec, sample_rate, **adsr_params)
        
        return wave