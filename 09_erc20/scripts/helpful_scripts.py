from brownie import (
    accounts, network, config
    )


FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    """
    Get account based on the environment.
    If 'index!=None' get a specific account from ganache-cli testnet accounts
    If 'index!=None' get an account configured on brownie accounts
    If network in "local chains", get an account its accounts
    else get an account from config/.env
    """
    if index:
        return accounts[index]
    if id:
        return accounts.load(id) 
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        # load from any local or forked environments
        return accounts[0] 
    # default method, load from the config file
    return accounts.add(config["wallets"]["from_key"])
