# music_engine/dsp.py

import numpy as np

def apply_delay(wave, sample_rate, delay_time=0.5, decay=0.5):
    
    print(f"Applying delay: {delay_time}s with {decay} decay...")
    
    # Calculate the delay in samples
    delay_samples = int(delay_time * sample_rate)
    
    # Create a new array long enough to hold the original wave and the echo tail
    output_wave = np.zeros(len(wave) + delay_samples)
    
    # 1. Add the original ("dry") signal
    output_wave[:len(wave)] = wave
    
    # 2. Add the delayed and decayed ("wet") signal
    output_wave[delay_samples:] += wave * decay
    
    # --- Normalization to prevent clipping ---
    peak_amplitude = np.max(np.abs(output_wave))
    if peak_amplitude > 1.0:
        output_wave /= peak_amplitude
        
    return output_wave

def apply_low_pass_filter(wave, sample_rate, cutoff_freq=1000):
    """
    Applies a simple low-pass filter to a wave.

    Args:
        wave (numpy.ndarray): The input audio wave.
        sample_rate (int): The sample rate of the audio.
        cutoff_freq (int): The frequency (in Hz) above which to cut.

    Returns:
        numpy.ndarray: The filtered wave.
    """
    # This is the math for a simple first-order IIR low-pass filter
    rc = 1.0 / (cutoff_freq * 2 * np.pi)
    dt = 1.0 / sample_rate
    alpha = dt / (rc + dt)
    
    # Create an empty array for the output
    filtered_wave = np.zeros_like(wave)
    # The filter's memory of the last sample
    filtered_wave[0] = alpha * wave[0]
    
    # Loop through the wave and apply the filter formula
    for i in range(1, len(wave)):
        filtered_wave[i] = alpha * wave[i] + (1 - alpha) * filtered_wave[i-1]
        
    return filtered_wave


def apply_high_pass_filter(wave, sample_rate, cutoff_freq=1000):
    """
    Applies a simple high-pass filter to a wave.

    Args:
        wave (numpy.ndarray): The input audio wave.
        sample_rate (int): The sample rate of the audio.
        cutoff_freq (int): The frequency (in Hz) below which to cut.

    Returns:
        numpy.ndarray: The filtered wave.
    """
    # A high-pass filter can be created by subtracting the low-pass
    # version of the signal from the original signal.
    low_pass = apply_low_pass_filter(wave, sample_rate, cutoff_freq)
    high_pass = wave - low_pass
    
    return high_pass


# In music_engine/dsp.py, add this function

def apply_reverb(wave, sample_rate, room_size=0.8, decay=0.7, dry_wet_mix=0.3):
    """
    Applies a reverb effect based on the Schroeder reverberator model.

    Args:
        wave (numpy.ndarray): The input audio wave.
        sample_rate (int): The sample rate of the audio.
        room_size (float): Simulates the room size (0.0 to 1.0). Affects delay times.
        decay (float): The decay factor of the reverb tail (0.0 to 1.0).
        dry_wet_mix (float): The mix between original (dry) and reverb (wet) signal. 0.0 is all dry, 1.0 is all wet.

    Returns:
        numpy.ndarray: The wave with the reverb effect applied.
    """
    # --- Helper functions for the reverb components ---
    def comb_filter(input_wave, delay_samples, feedback):
        output = np.zeros_like(input_wave)
        delay_buffer = np.zeros(delay_samples)
        for i in range(len(input_wave)):
            delayed_sample = delay_buffer[0]
            delay_buffer = np.roll(delay_buffer, -1)
            delay_buffer[-1] = input_wave[i] + delayed_sample * feedback
            output[i] = delayed_sample
        return output

    def all_pass_filter(input_wave, delay_samples, gain=0.5):
        output = np.zeros_like(input_wave)
        delay_buffer = np.zeros(delay_samples)
        for i in range(len(input_wave)):
            delayed_sample = delay_buffer[0]
            delay_buffer = np.roll(delay_buffer, -1)
            
            input_plus_gain = input_wave[i] + delayed_sample * gain
            delay_buffer[-1] = input_plus_gain
            output[i] = -input_wave[i] * gain + delayed_sample
        return output

    # --- Reverb parameters based on Schroeder's recommendations ---
    # Delay times are chosen to be mutually prime
    comb_delays = [int(d * room_size * sample_rate) for d in [0.0297, 0.0371, 0.0411, 0.0437]]
    all_pass_delays = [int(d * room_size * sample_rate) for d in [0.005, 0.0017]]
    
    # --- Apply comb filters in parallel ---
    wet_signal = np.zeros_like(wave)
    for delay in comb_delays:
        wet_signal += comb_filter(wave, delay, decay)
    
    # --- Apply all-pass filters in series to diffuse the sound ---
    for delay in all_pass_delays:
        wet_signal = all_pass_filter(wet_signal, delay)

    # --- Mix the dry and wet signals ---
    # Normalize wet signal before mixing
    peak_wet = np.max(np.abs(wet_signal))
    if peak_wet > 1.0:
        wet_signal /= peak_wet

    final_output = (1 - dry_wet_mix) * wave + dry_wet_mix * wet_signal

    # Final normalization
    peak_final = np.max(np.abs(final_output))
    if peak_final > 1.0:
        final_output /= peak_final
        
    return final_output