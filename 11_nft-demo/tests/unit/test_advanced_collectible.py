from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract
from scripts.advanced_collectible.deploy_and_create import deploy_and_create
from brownie import network
import pytest



def test_can_create_advanced_collectible():
    # deploy the contract
    # create an NFT
    # get a random breed back

    # ARRANGE
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")

    # ACT
    advanced_collectible, creating_tx = deploy_and_create()

    # We need to simulate chainlink VRFCoordinator call:
    
    # get 'reguestedId' from the emitted 'event' from 'createCollectible' 
    # in order to be able to get "random number" in the following steps 
    request_id = creating_tx.events["requestedCollectible"]["requestId"]

    # in local ganache, there is no LINK node, thus we need to dummy the response from the 
    # chainlink node via callBack function, i.e. callBackWithRandomness, (=pretend we are VRF coordinator)
    STATIC_RANDOM_NUMBER = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, 
        STATIC_RANDOM_NUMBER, 
        advanced_collectible.address, 
        {"from": get_account()},
    )

    # ASSERT
    assert advanced_collectible.tokenCounter() == 1
    assert advanced_collectible.tokenIdToBreed(0) == STATIC_RANDOM_NUMBER % 3