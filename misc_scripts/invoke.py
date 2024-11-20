import sys, os
from dotenv import load_dotenv
from requests import post

load_dotenv()

def main():
    url = os.getenv("HTTP_ENDPOINT")
    num_invokes = int(sys.argv[1])

    for i in range(1, num_invokes+1):
        file_path = f"../audioFiles/invocation_analysis/audio_file_{i}.mp3"
        # Open the file in binary mode
        with open(file_path, 'rb') as file:
            # Create a dictionary for the file to be sent as part of the multipart/form-data
            files = {'file': (os.path.basename(file_path), file)}

            try:
                res = post(
                    url=url,
                    files=files
                )

                res.raise_for_status()
                print(res.text)
            except Exception as e:
                print("ERROR:", e)
                sys.exit(-1)

if __name__ == "__main__":
    main()