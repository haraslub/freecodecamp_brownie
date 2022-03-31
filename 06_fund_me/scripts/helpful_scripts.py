from brownie import config, accounts, network, MockV3Aggregator
from web3 import Web3

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_NETWORKS = ["development", "ganache-local"]

DECIMAL = 8
STARTING_PRICE = 200000000000


def get_account():
    if (network.show_active() in LOCAL_BLOCKCHAIN_NETWORKS
     or network.show_active() in FORKED_LOCAL_ENVIRONMENTS):
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


def deploy_mocks():
    print("The active network is {}".format(network.show_active()))
    print("Deploying Mocks...")
    if len(MockV3Aggregator) <= 0:
        MockV3Aggregator.deploy(
            DECIMAL, 
            # Web3.toWei(STARTING_PRICE, "ether"),
            STARTING_PRICE, 
            {"from": get_account()},
        )
    print("Mocks deployed!")