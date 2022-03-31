from scripts.helpful_scripts import get_account, get_contract, fund_with_link, OPENSEA_URL
from brownie import AdvancedCollectible, network, config

sample_token_uri = "https://ipfs.io/ipfs/Qmd9MCGtdVz2miNumBHDbvj8bigSgTwnr4SbyH6DNnpWdt?filename=0-PUG.json"


def deploy_and_create():
    account = get_account()
    # If on testnet, used deployed contracts, otherwise deploy some mocks and use those
    advanced_collectible = AdvancedCollectible.deploy(
        get_contract("vrf_coordinator"),
        get_contract("link_token"),
        config["networks"][network.show_active()]["keyhash"],
        config["networks"][network.show_active()]["fee"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    # fund the 'advanced_collectible' contract with LINK
    fund_with_link(advanced_collectible.address)
    # create collectible token
    creating_tx = advanced_collectible.createCollectible({"from": account})
    # wait one block to confi rm
    creating_tx.wait(1)
    print("New token has been created!")
    return advanced_collectible, creating_tx


def main():
    deploy_and_create()