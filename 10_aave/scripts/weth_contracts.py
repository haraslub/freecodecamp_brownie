from scripts.helpful_scripts import get_account
from brownie import interface, config, network


def get_weth():
    """
    Mints WETH by depositing ETH.
    """
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.1 * 10**18})
    tx.wait(1)
    print("Received 0.1 WETH")
    return tx


def withdraw_eth():
    """
    Withdraw ETH from WETH.
    """
    account = get_account()
    eth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = eth.withdraw(0.1 * 10**18, {"from": account})
    tx.wait(1)
    print("Received 0.1 ETH")
    return tx


# def main():
#     get_weth()
#     # withdraw_eth()
