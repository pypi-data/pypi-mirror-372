# music_engine/arrangement.py

import numpy as np

class Arrangement:
    def __init__(self, tempo, sample_rate=44100):
        
        self.tempo = tempo
        self.sample_rate = sample_rate
        self.notes_on_timeline = [] # Stores (start_beat, note_object)

    def add_note(self, note, start_beat):
        
        self.notes_on_timeline.append((start_beat, note))

    def render(self, waveform='sine', adsr_params=None):
        
        # Calculate timing conversions
        seconds_per_beat = 60.0 / self.tempo
        
        # Find the end time of the last note to determine total duration
        total_duration_beats = 0
        for start_beat, note in self.notes_on_timeline:
            end_beat = start_beat + note.duration
            if end_beat > total_duration_beats:
                total_duration_beats = end_beat
        
        total_duration_sec = total_duration_beats * seconds_per_beat
        total_samples = int(total_duration_sec * self.sample_rate)
        
        # Create a silent master track
        master_track = np.zeros(total_samples, dtype=np.float64)

        # Render and mix each note
        for start_beat, note in self.notes_on_timeline:
            # Render the individual note
            note_wave = note.render(self.tempo, self.sample_rate, waveform, adsr_params)
            
            # Calculate its start position in samples
            start_sample = int(start_beat * seconds_per_beat * self.sample_rate)
            end_sample = start_sample + len(note_wave)
            
            
            if end_sample <= len(master_track):
                master_track[start_sample:end_sample] += note_wave

        # --- Normalization to prevent clipping ---
        peak_amplitude = np.max(np.abs(master_track))
        if peak_amplitude > 1.0:
            master_track /= peak_amplitude
            
        print("Arrangement rendered and normalized.")
        return master_track