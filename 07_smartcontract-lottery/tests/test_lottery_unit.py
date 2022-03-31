from brownie import Lottery, accounts, network, config, exceptions
from scripts.deploy_lottery import deploy_lottery, get_account, get_contract
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, fund_with_link
from web3 import Web3
import pytest


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip
    # Arrange
    lottery = deploy_lottery()
    # Act
    # 2000 ETH/USD; usdEntryFee is 50 USD; prices for the test environment?
    expected_entrance_fee = Web3.toWei(50/2000, "ether")
    print("expected: {}".format(expected_entrance_fee))
    entrance_fee = lottery.getEntranceFee()
    print("real: {}".format(entrance_fee))
    # Assert
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip
    lottery = deploy_lottery()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    # Act
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip
    lottery = deploy_lottery()
    account = get_account()
    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery) # to be able to end lottery, link must be send to VRF at first
    lottery.endLottery({"from": account})
    # Assert
    assert lottery.lottery_state() == 2


# rather integration test than unit:
def test_can_pick_winner_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip
    lottery = deploy_lottery()
    account = get_account()
    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    tx = lottery.endLottery({"from": account})
    # get 'reguestedId' from 'event' from 'endLottery' in order to be able to get 
    # "random number" in the following steps
    request_id = tx.events["RequestedRandomness"]["requestId"]
    # in local ganache, there is no LINK node, thus we need to dummy the response from the 
    # chainlink node via callBack function (=pretend we are VRF coordinator)
    STATIC_RANDOM_NUMBER = 777 # set some number to substitute the real 'random' number
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RANDOM_NUMBER, lottery.address, {"from": account}
    )
    # balances for Assert no 2.
    lottery_balance = lottery.balance()
    account_balance = account.balance()
    # Assert
    # 1. check, if winner is correct; as 777 % 3 = 0, thus the winner is the account
    assert lottery.recentWinner() == account
    # 2. check the correctness of balances
    # 2.1 the balance of the lottery has to be zero
    assert lottery.balance() == 0
    # 2.2 the balance of the winner is correct
    assert account.balance() == lottery_balance + account_balance





