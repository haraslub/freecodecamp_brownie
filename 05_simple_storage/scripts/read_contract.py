from brownie import SimpleStorage, config, accounts


def read_value():
    simple_storage = SimpleStorage[-1]  # to get the most recent deployment use '-1'
    print(simple_storage.retrieve())
    print(SimpleStorage[0])             # get contract address
    # ABI
    # Address


def main():
    read_value()