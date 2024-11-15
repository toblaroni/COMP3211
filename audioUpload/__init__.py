import os
import logging

from dotenv import load_dotenv
import librosa

import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueClient, BinaryBase64DecodePolicy, BinaryBase64EncodePolicy

load_dotenv()

blob_service_client = BlobServiceClient.from_connection_string(os.getenv("STORAGE_CONNECTION_STRING"))
queue_client        = QueueClient.from_connection_string(os.getenv("STORAGE_CONNECTION_STRING"), queue_name="audio-upload-queue")

# Contains logic for recieving and storing an audio file...
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing audio file upload...")

    # Grab file from the request    
    audio_file = req.files.get("file")
    if not audio_file:
        return func.HttpResponse("Expected an audio file.", status_code=400)
    
    # Use librosa to check that the file can actually be uploaded
    try:
        librosa.load(path=audio_file, sr=None)
    except Exception as e:
        return func.HttpResponse(
            f"Invalid audio file. Error: {e}", 
            status_code=400
        )
    
    try:
        # Reset file stream
        audio_file.stream.seek(0)

        logging.info("Attempting to upload file to blob storage...")

        # Store the audio file in a blob
        blob_client = blob_service_client.get_blob_client(container="audio-uploads", blob=f"{audio_file.filename}")
        blob_client.upload_blob(audio_file.stream, overwrite=True)

        queue_client.message_encode_policy = BinaryBase64EncodePolicy()
        queue_client.message_decode_policy = BinaryBase64DecodePolicy()

        filename_bytes = f"{audio_file.filename}".encode("ascii")

        # This should trigger second function
        queue_client.send_message(
            queue_client.message_encode_policy.encode(content=filename_bytes)
        )  

        logging.info("Upload successful.")

        return func.HttpResponse(
            f"\"{audio_file.filename}\" uploaded successfully.",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            f"Error occurred while uploading audio file. Error: {e}", 
            status_code=500
        )
