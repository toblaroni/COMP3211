import os
import logging

import librosa
import azure.functions as func

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
            f"Unable to load audio file. Error: {e}", 
            status_code=400
        )
    
    ### Store audio file in some sort of blob or something

    return func.HttpResponse(
        f"{audio_file.filename} uploaded successfully.",
        status_code=200
    )