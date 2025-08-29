import numpy as np
from src.music_engine.dsp import apply_delay

def test_apply_delay_output_length():
    
    wave = np.zeros(1000) # 1000 samples long
    sample_rate = 44100
    delay_time = 0.1 # seconds
    
    # Calculate the expected number of delay samples
    delay_samples = int(delay_time * sample_rate)
    expected_length = len(wave) + delay_samples

    # Run the function
    delayed_wave = apply_delay(wave, sample_rate, delay_time)
    
    # Assertthat the result is what we expect
    assert len(delayed_wave) == expected_length