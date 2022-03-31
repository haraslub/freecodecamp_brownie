from brownie import accounts, config, SimpleStorage, network
import os


def get_account():
    if network.show_active() == "development":
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


def deploy_simple_storage():
    # account = accounts[0]                                 # it works only with ganache-cli
    # account = accounts.load("freecodecamp-account")       # get account which we defined from Brownie // HIGHLY RECOMMENDED
                                                            # WAY TO STORE PRIVATE KEY (ENCRYPTED + PASSWORD)
    # account = accounts.add(os.getenv("PRIVATE_KEY"))      # get private_key from env 
    # account = accounts.add(config["wallets"]["from_key"]) # get private_key from env via config
    account = get_account()
    simple_storage = SimpleStorage.deploy({"from": account})
    stored_value = simple_storage.retrieve()
    print(stored_value)
    transaction = simple_storage.store(15, {"from": account})   # need to be add who we are going to transact from
    transaction.wait(1)     # wait 1 block
    updated_simple_storage = simple_storage.retrieve()
    print(updated_simple_storage)


def main():
    deploy_simple_storage()