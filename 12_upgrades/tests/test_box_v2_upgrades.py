from scripts.helpful_scripts import get_account, deploy_proxy, upgrade
from brownie import Box, BoxV2, Contract, exceptions, config, network
import pytest


def test_proxy_upgrades():
    account = get_account()
    
    box = Box.deploy({"from": account}, publish_source=config["networks"][network.show_active()].get("publish", False))
    proxy_admin, proxy_box, proxy = deploy_proxy(account, box, "Box")
    # ACT 1 - deploy box V2 and use proxy box V2 without upgrade
    #   test will pass if VirtualMachineError
    box_V2 = BoxV2.deploy({"from": account}, publish_source=config["networks"][network.show_active()].get("publish", False))
    proxy_box_V2 =Contract.from_abi(
        "BoxV2", proxy.address, BoxV2.abi,
    )
    # ASSERT 1
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_box_V2.increment({"from": account})
    # ACT 2 - upgrade proxy, test its functions
    upgrade_box = upgrade(
        account,
        proxy,
        box_V2.address,
        proxy_admin_contract = proxy_admin,
    )
    upgrade_box.wait(1)

    proxy_box_V2 =Contract.from_abi(
        "BoxV2", proxy.address, BoxV2.abi,
    )
    # ASSERT
    assert proxy_box_V2.retrieve() == 0

    proxy_box_V2.store(1, {"from": account})
    assert proxy_box_V2.retrieve() == 1

    proxy_box_V2.increment({"from": account})
    assert proxy_box_V2.retrieve() == 2

