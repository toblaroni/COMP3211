import logging
import io
import os
import json
from pathlib import Path

from dotenv import load_dotenv
import librosa
import numpy as np

from azure.functions import QueueMessage
from azure.storage.blob import BlobServiceClient

load_dotenv()

blob_service_client = BlobServiceClient.from_connection_string(os.getenv("STORAGE_CONNECTION_STRING"))

def main(msg: QueueMessage) -> None:
    filename = msg.get_body().decode("utf-8")

    blob_client = blob_service_client.get_blob_client(container="audio-uploads", blob=filename)

    # Create IO stream
    audio_stream = io.BytesIO()
    blob_client.download_blob().download_to_stream(audio_stream)    # This downloads it as a stream

    audio_stream.seek(0)

    # Load audio
    y, sr = librosa.load(audio_stream, sr=None)

    # Basic Analysis
    duration = librosa.get_duration(y=y, sr=sr)

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    # Make sure that tempo is a float
    tempo = float(tempo) if isinstance(tempo, (int, float, np.number)) else 0.0

    # Pitch
    pitches, _ = librosa.piptrack(y=y, sr=sr)
    pitch_values = pitches[pitches > 0]
    average_pitch = pitch_values.mean() if len(pitch_values) > 0 else 0

    # Brightness (Spectral Centroid)
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
    brightness = spectral_centroids.mean()

    # Harmonic / percussive components
    harmonic, percussive = librosa.effects.hpss(y)
    harmonic_energy = np.sum(harmonic ** 2)
    percussive_energy = np.sum(percussive ** 2)

    # Spectral bandwidth and contrast
    # Useful for analyzing the audios "fullness" and "texture"
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr).mean()
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr).mean()

    # Onset strength
    # Useful for identifying transitions in the music
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_strength = onset_env.mean()

    # Zero-crossing rate
    # Tells us about noisiness / sharpness of sound
    zcr = librosa.feature.zero_crossing_rate(y=y).mean()

    # Harmonic complexity
    # Useful for genre classification
    tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr)
    tonnetz_mean = tonnetz.mean()

    json_data = {
        "name": filename,
        "duration": float(duration),
        "tempo": tempo,
        "average_pitch": float(average_pitch),
        "brightness": float(brightness),
        "harmonic_energy": float(harmonic_energy),
        "percussive_energy": float(percussive_energy),
        "spectral_bandwidth": float(spectral_bandwidth),
        "spectral_contrast": float(spectral_contrast),
        "onset_strength": float(onset_strength),
        "zero_crossing_rate": float(zcr),
        "harmonic_complexity": float(tonnetz_mean)
    }

    file_no_ext = Path(filename).stem

    # Upload results to Blob storage
    result_blob_client = blob_service_client.get_blob_client(
        container="audio-analysis-results", 
        blob=f"{file_no_ext}-analysis.json"
    )

    result_blob_client.upload_blob(json.dumps(json_data), overwrite=True)

    logging.info(f"==== Finished analyzing {filename} ====")
    logging.info(f"Duration: {duration} seconds")
    logging.info(f"Tempo: {tempo} BPM")
    logging.info(f"Average Pitch: {average_pitch} Hz")
    logging.info(f"Brightness: {brightness} Hz")
    logging.info(f"Harmonic Energy: {harmonic_energy}")
    logging.info(f"Percussive Energy: {percussive_energy}")
    logging.info(f"Spectral Bandwidth: {spectral_bandwidth}")
    logging.info(f"Spectral Contrast: {spectral_contrast}")
    logging.info(f"Onset Strength: {onset_strength}")
    logging.info(f"Zero-Crossing Rate: {zcr}")
    logging.info(f"Harmonic Complexity (Tonnetz): {tonnetz_mean}")
