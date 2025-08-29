# music_engine/wave_writer.py

import struct
import numpy as np

def write_wav(filepath, data, sample_rate=44100):
    """
    Writes a NumPy array to a 16-bit mono WAV file.

    This function writes the WAV file from scratch, demonstrating
    understanding of the file format.

    Args:
        filepath (str): The path to the output WAV file.
        data (numpy.ndarray): The audio data (should be floats from -1.0 to 1.0).
        sample_rate (int): The sample rate in Hz.
    """
    # 1. Convert float data to 16-bit integers
    data_int16 = np.int16(data * 32767)

    # 2. Define WAV file parameters
    num_channels = 1  # Mono
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    num_samples = len(data_int16)
    data_size = num_samples * block_align

    with open(filepath, 'wb') as f:
        # ---- The RIFF chunk descriptor ----
        f.write(b'RIFF')
        # ChunkSize: 36 + data_size
        f.write(struct.pack('<I', 36 + data_size))
        f.write(b'WAVE')

        # ---- The "fmt " sub-chunk ----
        f.write(b'fmt ')
        # Subchunk1Size: 16 for PCM
        f.write(struct.pack('<I', 16))
        # AudioFormat: 1 for PCM
        f.write(struct.pack('<H', 1))
        # NumChannels: 1 for mono
        f.write(struct.pack('<H', num_channels))
        # SampleRate
        f.write(struct.pack('<I', sample_rate))
        # ByteRate
        f.write(struct.pack('<I', byte_rate))
        # BlockAlign
        f.write(struct.pack('<H', block_align))
        # BitsPerSample
        f.write(struct.pack('<H', bits_per_sample))

        # ---- The "data" sub-chunk ----
        f.write(b'data')
        # Subchunk2Size: data_size
        f.write(struct.pack('<I', data_size))
        # The actual sound data
        f.write(data_int16.tobytes())

    print(f"Wrote WAV file to {filepath} using custom writer.")