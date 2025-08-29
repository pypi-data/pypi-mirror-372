# music_engine/synthesis.py

import numpy as np

def generate_wave(waveform, frequency, duration, sample_rate=44100, amplitude=0.5):
    """
    Generates a wave of a specified type.

    Args:
        waveform (str): Type of waveform ('sine', 'square', 'sawtooth', 'triangle').
        frequency (float): Frequency of the wave in Hz.
        duration (float): Duration of the wave in seconds.
        sample_rate (int): The sample rate in Hz.
        amplitude (float): The amplitude of the wave (0.0 to 1.0).

    Returns:
        numpy.ndarray: The generated wave.
    """
    t = np.linspace(0., duration, int(sample_rate * duration), endpoint=False)
    
    # The fundamental formula is 2 * pi * frequency * t
    # This represents the angle (in radians) of the wave at each point in time.
    angular_freq = 2 * np.pi * frequency * t

    wave = None
    
    if waveform == 'sine':
        wave = np.sin(angular_freq)
    
    elif waveform == 'square':
        # Creates a square wave by taking the sign of a sine wave
        wave = np.sign(np.sin(angular_freq))
        
    elif waveform == 'sawtooth':
        # Creates a sawtooth wave that ramps from -1 to 1
        # (t * freq) % 1 gives a 0-1 ramp, then we scale and shift it
        wave = 2 * (t * frequency - np.floor(0.5 + t * frequency))
        
    elif waveform == 'triangle':
        # Creates a triangle wave using the arcsin of a sine wave
        wave = (2 / np.pi) * np.arcsin(np.sin(angular_freq))
        
    else:
        raise ValueError("Unsupported waveform type")

    return amplitude * wave

# Add this function to music_engine/synthesis.py

# In music_engine/synthesis.py

def apply_adsr_envelope(wave, duration, sample_rate=44100, attack_time=0.01, decay_time=0.05, sustain_level=0.7, release_time=0.2):
    """
    Applies a more robust ADSR envelope to a wave, handling short notes correctly.
    """
    total_samples = len(wave)
    if total_samples == 0:
        return wave
        
    envelope = np.zeros(total_samples)

    # Calculate sample counts for each phase
    attack_samples = int(attack_time * sample_rate)
    decay_samples = int(decay_time * sample_rate)
    release_samples = int(release_time * sample_rate)

    # Define indices for each phase of the envelope
    attack_end_idx = min(attack_samples, total_samples)
    
    # Release always happens at the end
    release_start_idx = max(attack_end_idx, total_samples - release_samples)
    
    decay_end_idx = min(attack_end_idx + decay_samples, release_start_idx)

    # 1. Attack Phase
    if attack_end_idx > 0:
        envelope[:attack_end_idx] = np.linspace(0, 1, attack_end_idx, endpoint=False)

    # 2. Decay Phase
    if decay_end_idx > attack_end_idx:
        envelope[attack_end_idx:decay_end_idx] = np.linspace(1, sustain_level, decay_end_idx - attack_end_idx, endpoint=False)

    # 3. Sustain Phase
    if release_start_idx > decay_end_idx:
        envelope[decay_end_idx:release_start_idx] = sustain_level

    # 4. Release Phase
    if total_samples > release_start_idx:
        # What's the volume level when release starts?
        release_start_level = sustain_level
        if release_start_idx > decay_end_idx:
             release_start_level = sustain_level
        elif release_start_idx > attack_end_idx:
             # Release starts during decay
             # Interpolate to find the current level
             decay_progress = (release_start_idx - attack_end_idx) / decay_samples
             release_start_level = 1 - (1 - sustain_level) * decay_progress
        else:
             # Release starts during attack
             attack_progress = release_start_idx / attack_samples
             release_start_level = attack_progress

        envelope[release_start_idx:] = np.linspace(release_start_level, 0, total_samples - release_start_idx, endpoint=False)
    
    return wave * envelope