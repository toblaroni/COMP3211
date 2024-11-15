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

    # Create IO stream
    audio_stream = io.BytesIO(blob_data.readall())

    # We can now use librosa to read cool shit about the audio file
    y, sr = librosa.load(audio_stream, sr=None)

    logging.info(f"\n\nSample rate: {sr}")
    logging.info(f"Audio data shape: {y.shape}\n\n")