import os, requests
from pathlib import Path


def upload_to_pinata(filepath):
    PINATA_BASE_URL = "https://api.pinata.cloud"
    endpoint = "/pinning/pinFileToIPFS"
    # to post to PINATA, headers must be added, more info at:
    #  https://docs.pinata.cloud/api-pinning/pin-file 
    headers = {
        "pinata_api_key": os.getenv("PINATA_API_KEY"),
        "pinata_secret_api_key": os.getenv("PINATA_API_SECRET")
    }
    filename = filepath.split("/")[-1:][0]

    with Path(filepath).open("rb") as fp:
        image_binary = fp.read()
        response = requests.post(
            PINATA_BASE_URL + endpoint,
            files={"file": (filename, image_binary)},
            headers=headers
        )
        print(response.json())


def main():
    upload_to_pinata("./img/pug.png")
