from scripts.helpful_scripts import get_account, get_contract, fund_with_link
from brownie import Lottery
from brownie import config, network
import time


def deploy_lottery():
    account = get_account()
    # account = get_account(id="freecodecamp-account")
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False), 
    )
    print("Deployed lottery by the contract {}".format(account))
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1) # to wait until TX is finilized;
    print("Lottery is started!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 10000 # add 10000 (barely nothing) to be save it passes
    tx = lottery.enter({"from": account, "value": value}) # add value as we need to send some value: see msg.value in enter()
    tx.wait(1)
    print("You entered the lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # fund the contract with LINK tokens
    # the end the lottery
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    time.sleep(300) # due to interaction with LINK node, need to wait for response (increased from 60 to 300 as the
    # winner was not picked correctly (0x000...000))
    print("{} is the new lottery winner!".format(lottery.recentWinner()))
    print("Lottery ended successfully.")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()