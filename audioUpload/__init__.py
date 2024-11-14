import os
import logging
from dotenv import load_dotenv
import librosa
import azure.functions as func
from azure.storage.blob import BlobServiceClient

load_dotenv()

blob_service_client = BlobServiceClient.from_connection_string(os.getenv("STORAGE_CONNECTION_STRING"))

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

        # Store the audio file in a blob
        blob_client = blob_service_client.get_blob_client(container="audio-uploads", blob="uploaded_file")
        blob_client.upload_blob(audio_file.stream, overwrite=True)

        return func.HttpResponse(
            f"\"{audio_file.filename}\" uploaded successfully.",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            f"Error occurred while uploading audio file. Error: {e}", 
            status_code=500
        )
