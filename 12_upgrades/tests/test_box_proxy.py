from scripts.helpful_scripts import get_account, encode_function_data, deploy_proxy
from brownie import Box, ProxyAdmin, TransparentUpgradeableProxy, Contract


def test_proxy_delegates_calls():
    # Arrange
    account = get_account()
    box = Box.deploy({"from": account})
    # Act
    (proxy_admin, proxy_box, proxy) = deploy_proxy(account, box, "Box")
    # Assert
    assert proxy_box.retrieve() == 0
    proxy_box.store(1, {"from": account})
    assert proxy_box.retrieve() == 1


