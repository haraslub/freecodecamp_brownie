from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS
from scripts.advanced_collectible.deploy_and_create import deploy_and_create
from brownie import network
import pytest, time



def test_can_create_advanced_collectible_integration():
    # deploy the contract
    # create an NFT
    # get a random breed back

    # ARRANGE
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for integration testing")

    # ACT
    advanced_collectible, creating_tx = deploy_and_create()
    time.sleep(300)

    # ASSERT
    assert advanced_collectible.tokenCounter() == 1
