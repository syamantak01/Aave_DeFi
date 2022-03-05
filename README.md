# DeFi Application

This is a DeFi Application built with Aave, Chainlink and Brownie.

## Overall steps

   1. swap ETH for WETH
   2. Deposit some ETH(in our case, WETH) into Aave
   3. Borrow some asset with ETH collateral
      1. Sell that borrowed asset (short selling)
   4. Repay everything back.

First, we need some WETH and to get WETH we can interact with the [WETH token contract](https://kovan.etherscan.io/token/0xd0a1e359811322d97991e03f863a0c30c2cf029c#writeContract)

to interact with a contract, we need :

- ABI
- Contract Address

one simple way to do is by declaring an Interface.
interfaces->IWeth.sol

Now that we have WETH, we can start working on the borrowing function

We can interact with aave protocols:
-ILendingPoolAddressesProvider interface
-ILendingPool interface

We can take the wrappedETH and deposit into the contract obtained through the lending_pool
Before depositing, we need to *approve* the ERC20 token/WETH. Done with the `approve()`.For that we use IERC20 interface

Now we can deposit using the `depsit()` method of *lending_pool*

Before we can borrow, we need to know how much we can borrow. We can get the user account information with the `getUserAccountData()` method which can be used to find **total Collateral**, **total Debt**, **how much available ETH can I borrow**.

Now we can borrow some DAI, but we need to get conversation rates(DAI->ETH) in order to get the uniformity. And for that we need to use chainlink datafeeds. We can borrow certain allowable amount of DAI.

Now after borrowing, we will work on repaying that back:

- First thing to do is to call the approve function and we are going to prove that we are going to pay back
- then use repay() method to reopay the amount borrowed
