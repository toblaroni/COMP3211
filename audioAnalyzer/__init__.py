import logging
import io
import os

from dotenv import load_dotenv
import librosa

from azure.functions import QueueMessage
from azure.storage.blob import BlobServiceClient

load_dotenv()

blob_service_client = BlobServiceClient.from_connection_string(os.getenv("STORAGE_CONNECTION_STRING"))

def main(msg: QueueMessage) -> None:
    filename = msg.get_body().decode("utf-8")

    blob_client = blob_service_client.get_blob_client(container="audio-uploads", blob=filename)
    blob_data = blob_client.download_blob()     # Download the blob

    # create IO stream
    audio_stream = io.BytesIO(blob_data.readall())

    # We can now use librosa to read cool stuff about the audio file
    y, sr = librosa.load(audio_stream, sr=None)

    duration = librosa.get_duration(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    pitches, _ = librosa.piptrack(y=y, sr=sr)
    # filter non zero pitches
    pitch_values = pitches[pitches > 0]
    average_pitch = pitch_values.mean() if len(pitch_values) > 0 else 0

    # Brightness
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
    brightness = spectral_centroids.mean()

    logging.info(f"==== Finished analyzing {filename} ====")
    logging.info(f"Duration: {round(duration)} seconds")
    logging.info(f"Tempo: {round(tempo)}BPM")
    logging.info(f"Pitch: {round(average_pitch)}Hz")
    logging.info(f"Center of Mass (Brightness): {round(brightness)}Hz")