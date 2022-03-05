from scripts.utils import get_account
from brownie import interface
from brownie import network, config, interface


def main():
    get_weth()


def get_weth():
    """
    Mints WETH by depositing ETH

    """
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18})
    tx.wait(1)
    print("Received 0.1 WETH")
    return tx
