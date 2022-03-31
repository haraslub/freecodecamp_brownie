from scripts.helpful_scripts import encode_function_data, get_account, upgrade
from brownie import (
    network, Contract, config, 
    Box, ProxyAdmin, TransparentUpgradeableProxy, BoxV2
)


def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    
    # DEPLOY THE CONTRACT
    box = Box.deploy({"from": account}, publish_source=config["networks"][network.show_active()].get("verify", False))
    print(box.retrieve())

    # DEPLOY THE PROXY ADMIN
    proxy_admin = ProxyAdmin.deploy(
        {"from": account}, 
        publish_source=config["networks"][network.show_active()].get("verify", False)
        )

    # 1) we need to encode 'initializer' function
    #  -> initializer = box.store, 1 -> we need to encode it in bytes for our PROXY
    # box_encoded_initializer_function = encode_function_data(initializer)
    # we encode nothing to our initializer (we use blank initializer)
    box_encoded_initializer_function = encode_function_data()

    # DEPLOY THE PROXY
    proxy = TransparentUpgradeableProxy.deploy(
        box.address, # address of our contract (=_logic in the constructor)
        proxy_admin.address, # an adress of admin (= admin_ in the constructor)
        box_encoded_initializer_function, # initializor (can be blank) (= _data in the constructor)
        {"from": account, "gas_limit": 1000000}, # sometimes, the proxy has hard time with gas limits
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print(f"Proxy deployed to {proxy}, you can now upgrade to V2!")

    # to be able to call on proxy address functions from the box contract, we need to assign ABI of the
    #   box contract to the proxy address; then the proxy will delegate all the calls to the box contract,
    #   which cannot be changed (proxy can be)
    proxy_box = Contract.from_abi(
        "Box",  # the name
        proxy.address,
        Box.abi,
    )
    print(proxy_box.retrieve())  # it will retrieve 0
    proxy_box.store(1, {"from": account})
    print(proxy_box.retrieve())  # it will retrieve 1
    
    # UPGRADING THE CONTRACT
    box_v2 = BoxV2.deploy({"from": account})
    upgrade_tx = upgrade(
        account,
        proxy,
        box_v2.address,
        proxy_admin_contract = proxy_admin,
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    upgrade_tx.wait(1)
    print("Proxy has been upgraded!")
    # and again, assign ABI of the BoxV2 contract to the proxy address
    proxy_box = Contract("BoxV2", proxy.address, BoxV2.abi)
    # we upgraded the contract, but our value (1) is stored in storage of proxy, thus
    #   we can increment to value=2:
    proxy_box.increment({"from": account})
    print(proxy_box.retrieve())