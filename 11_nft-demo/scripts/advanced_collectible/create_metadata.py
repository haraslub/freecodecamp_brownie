from brownie import AdvancedCollectible, network
from scripts.helpful_scripts import get_breed
from metadata.sample_metadata import metadata_template
from pathlib import Path
import requests, json, os

breed_to_image_uri = {
    "PUG": "https://ipfs.io/ipfs/QmSsYRx3LpDAb1GZQm7zZ1AuHZjfbPkD6J7s9r41xu1mf8?filename=pug.png",
    "SHIBA_INU": "https://ipfs.io/ipfs/QmYx6GsYAKnNzZ9A6NvEKV9nf1VaDzJrqDR23Y8YSkebLU?filename=shiba-inu.png",
    "ST_BERNARD": "https://ipfs.io/ipfs/QmUPjADFGEKmfohdTaNcWhp7VGk26h5jXDA7v3VtTnTLcW?filename=st-bernard.png",
}


def main():
    advanced_collectible = AdvancedCollectible[-1]
    number_of_collectibles = advanced_collectible.tokenCounter()
    print(f"You have created {number_of_collectibles} collectibles.")

    for token_id in range(number_of_collectibles):
        breed = get_breed(advanced_collectible.tokenIdToBreed(token_id))
        metadata_file_name = (
            f"./metadata/{network.show_active()}/{token_id}-{breed}.json"
        )
        collectible_metadata = metadata_template

        if Path(metadata_file_name).exists():
            print(f"\n{metadata_file_name} already exists! Delete it to overwrite.")
        else:
            print(f"\nCreating Metadata file: {metadata_file_name}")
            # name
            collectible_metadata["name"] = breed
            # description
            collectible_metadata["description"] = f"An adorable {breed} pup!"

            # image
            image_path = "./img/" + breed.lower().replace("_", "-") + ".png"

            image_uri = None
            # set in .env if want to upload to IPFS:
            if os.getenv("UPLOAD_IMAGE_URI") == "true":
                image_uri = upload_to_ipfs(image_path)
            image_uri = image_uri if image_uri else breed_to_image_uri[breed]
            
            collectible_metadata["image"] = image_uri
            # create json file of metadata
            with open(metadata_file_name, "w") as file:
                json.dump(collectible_metadata, file)
            
            # set in .env if want to upload to IPFS:
            if os.getenv("UPLOAD_IMAGE_URI") == "true":
                upload_to_ipfs(metadata_file_name)


def upload_to_ipfs(filepath):
    """
    Open the image as binary ("br") and upload it to IPFS.
    !!! IPFS Deamon must be running in order to function properly:

    Args:
        filepath (string): file path to image;
    
    Returns:
        image_uri (string): link to the image uploaded to IPFS server.
    """
    # Open image as binary file:
    with Path(filepath).open("br") as fp:
        image_binary = fp.read()
        # upload to IPFS (before uploading, the IPFS Command line must be installed)
        # https://docs.ipfs.io/install/command-line/#system-requirements
        ipfs_url = "http://127.0.0.1:5001"
        endpoint = "/api/v0/add" # details: https://docs.ipfs.io/reference/http/api/#api-v0-add 
        # get a response from ipfs server
        response = requests.post(ipfs_url + endpoint, files={"file": image_binary})
        # get a Hash from the response; response converted to json structure
        ipfs_hash = response.json()["Hash"]
        # get file name "./img/0-PUG.png" -> "0-PUG.png":
        filename = filepath.split("/")[-1:][0]
        # create image URI:
        image_uri = "https://ipfs.io/ipfs/{}?filename={}".format(ipfs_hash, filename)
        print(image_uri)
        return image_uri