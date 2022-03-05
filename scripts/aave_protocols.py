from scripts.utils import get_account
from brownie import config, network, interface
from scripts.get_weth import get_weth
from web3 import Web3

AMOUNT = Web3.toWei(0.01, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]

    # we can call the get_weth() function in case we need some weth
    if network.show_active() == "mainnet-fork":
        get_weth()

    lending_pool = get_lending_pool()

    # Approve sending out ERC20 token
    approve_erc20(AMOUNT, lending_pool.address, erc20_address, account)

    print("Depositing...")
    tx = lending_pool.deposit(
        erc20_address, AMOUNT, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited")

    # get user account information
    total_debt, borrowable_eth = get_borrowable_data(lending_pool, account)

    # get conversation rates of DAI->ETH
    dai_to_eth = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    print(f"DAI_TO_ETH: {dai_to_eth}")
    print(f"Borrowable_ETH: {borrowable_eth}")

    # converting borrowable_ETH-> borrowable_DAI*95%
    amount_dai_to_borrow = (1 / dai_to_eth) * (
        borrowable_eth * 0.95
    )  # multiplying by 0.95 as a buffer, to make sure the health factor is "better"

    print(f"We are going to borrow {amount_dai_to_borrow} DAI")

    # Now we can borrow some DAI
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("Borrowed DAI successfully")

    # show new account information
    get_borrowable_data(lending_pool, account)

    # Now we will repay everything that we have borrowed
    # repay_all(amount_dai_to_borrow, lending_pool, account)
    print("Successfully Deposited, Borrowed and Repayed!!!")


def repay_all(amount, lending_pool, account, rate_code=1):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        rate_code,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repayed successfully!")


def get_asset_price(price_feed_address):
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    latest_price_with_decimal = Web3.fromWei(latest_price, "ether")
    print(f"The DAI/ETH price is {latest_price_with_decimal}")
    return float(latest_price_with_decimal)


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)

    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")

    print(f"{total_collateral_eth} worth of ETH deposited.")
    print(f"{total_debt_eth} worth of ETH borrowed.")
    print(f"{available_borrow_eth} worth of ETH can be borrowed.")

    return (float(total_debt_eth), float(available_borrow_eth))


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving the ERC-20 token")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved the ERC-20 token")
    return tx


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()

    lending_pool = interface.ILendingPool(lending_pool_address)

    return lending_pool
