from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_NETWORKS
from scripts.deploy import deploy_fund_me
from brownie import network, accounts, exceptions
import pytest


def test_can_fund_and_withdraw():
    # Arrange
    account = get_account()
    fund_me = deploy_fund_me()
    entrance_fee = fund_me.getEntranceFee() + 100 # + 100 just in case we need little bit more 
    # Act 1
    tx1 = fund_me.fund({"from": account, "value": entrance_fee})
    tx1.wait(1)
    # Assert 1
    assert fund_me.addressToAmountFunded(account.address) == entrance_fee
    # Act 2
    tx2 = fund_me.withdraw({"from": account})
    tx2.wait(1)
    # Assert 2
    assert fund_me.addressToAmountFunded(account.address) == 0


def test_only_owner_can_withdraw():
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip("only for local testing")
    fund_me = deploy_fund_me()
    bad_actor = accounts.add()
    with pytest.raises(exceptions.VirtualMachineError):
        fund_me.withdraw({"from": bad_actor})   # should not go through as OnlyOwner can withdraw funds
        


