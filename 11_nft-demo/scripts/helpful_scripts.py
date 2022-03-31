from brownie import (
    accounts, network, config, Contract,
    LinkToken, VRFCoordinatorMock, MockV3Aggregator, MockOracle,
)
from web3 import Web3


NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    "mainnet-fork",
]
OPENSEA_URL = "https://testnets.opensea.io/assets/{}/{}"
BREED_MAPPING = {0: "PUG", 1: "SHIBA_INU", 2: "ST_BERNARD"}


def get_breed(breed_number: int):
    return BREED_MAPPING[breed_number]


def get_account(index=None, id=None):
    """
    Get account (private key) to work with

    Args:
        index (int): index of account in a local ganache
        id (string): name of the account from 'brownie accounts list'

    Returns: 
        (string): private key of the account
    """
    if index:
        return accounts[index]  # use account with defined index from local ganache
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]  # use the first ganache account
    if id:
        return accounts.load(id)    # use our defined account in 'brownie accounts list' (id=name)
    return accounts.add(config["wallets"]["from_key"])  # use account from our environment


contract_to_mock = {"link_token": LinkToken, "vrf_coordinator": VRFCoordinatorMock}


def get_contract(contract_name):
    """
    To use this function, go to the brownie config and add a new entry for
    the contract that you want to be able to 'get'. Then add an entry in the in the variable 'contract_to_mock'.
        This script will then either:
            - Get a address from the config.
            - Or deploy a mock to use for a network that doesn't have it.
        Args:
            contract_name (string): This is the name that is refered to in the
            brownie config and 'contract_to_mock' variable.
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            Contract of the type specificed by the dictonary. This could be either
            a mock or the 'real' contract on a live network.
    """
    contract_type = contract_to_mock[contract_name]

    if network.show_active() in NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        try:
            contract_address = config["networks"][network.show_active()][contract_name]
            contract = Contract.from_abi(
                contract_type._name, contract_address, contract_type.abi
            )
        except KeyError:
            print(
                f"{network.show_active()} address not found, perhaps you should add it to the config or deploy mocks?"
            )
            print(
                f"brownie run scripts/deploy_mocks.py --network {network.show_active()}"
            )
    return contract


def deploy_mocks(decimals=18, initial_value=2000):
    """
    Use this script if you want to deploy mocks to a testnet.
    
    Args:
        decimals (int):
        initial_value (int):
    """
    print(f"The active network is {network.show_active()}")
    print("Deploying Mocks...")
    account = get_account()

    print("Deploying Mock Link Token...")
    link_token = LinkToken.deploy({"from": account})

    print("Deploying Mock Price Feed...")
    mock_price_feed = MockV3Aggregator.deploy(
        decimals, initial_value, {"from": account}
    )
    print(f"Deployed to {mock_price_feed.address}")

    print("Deploying Mock VRFCoordinator...")
    mock_vrf_coordinator = VRFCoordinatorMock.deploy(
        link_token.address, {"from": account}
    )
    print(f"Deployed to {mock_vrf_coordinator.address}")

    print("Deploying Mock Oracle...")
    mock_oracle = MockOracle.deploy(link_token.address, {"from": account})
    print(f"Deployed to {mock_oracle.address}")
    print("Mocks Deployed!")


def fund_with_link(
    contract_address, 
    account=None, 
    link_token=None, 
    amount=Web3.toWei(1, "ether")
):
    """
    Fund given contract with LINK in order to get a random number from VRF Coordinator

    Args:
        contract_address (string): the contract address to be funded
        account (string): the account to be used for fudning contract_address
        link_token (string): address of link token 
        amount (int): the amount (in WEI) to be send to fund the contract_address 
    """
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    funding_tx = link_token.transfer(contract_address, amount, {"from": account})
    funding_tx.wait(1)
    print(f"Funded {contract_address}")
    return funding_tx
