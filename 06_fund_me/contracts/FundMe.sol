// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6; 

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol"; 
import "@chainlink/contracts/src/v0.6/vendor/SafeMathChainlink.sol"; 

contract FundMe { 
     
    using SafeMathChainlink for uint256; // prevention against overflowing; 
     
    mapping(address => uint256) public addressToAmountFunded; 
    address public owner;  
    address[] public funders; // empty array to store all funders of the contract
    AggregatorV3Interface public priceFeed;
     
    constructor(address _priceFeed) public { 
        priceFeed = AggregatorV3Interface(_priceFeed); 
        owner = msg.sender; // once contract deployed the owner (us) is created  
    } 
     
    function fund() public payable { 
        // min value = 50 USD 
        uint256 minimumUSD = 50 * 10**18; // convert USD to WEI; 
        // check if amount sent is bigger than minimumUSD:  
        require(
            getConversionRate(msg.value) >= minimumUSD, 
            "You need to spend more ETH!"
            ); 
        addressToAmountFunded[msg.sender] += msg.value; 
        // once somebody funds contract, add him to the 'funder' array: 
        funders.push(msg.sender); 
    } 
     
    function getVersion() public view returns(uint256) { 
        return priceFeed.version(); 
    } 
     
    function getPrice() public view returns(uint256) { 
        (,int price,,,) = priceFeed.latestRoundData(); 
        return uint256(price) * 10000000000; // we want price USD in WEI, thus converted to 18 decimals; 
    } 

    // 1000000000 
    function getConversionRate(uint256 ethAmount) public view returns(uint256) { 
        uint256 ethPrice = getPrice(); 
        uint256 ethAmountInUsd = (ethPrice * ethAmount) / 1000000000000000000; // both are in WEI, thus conversation to GWEI 
        return ethAmountInUsd; 
    }

    function getEntranceFee() public view returns (uint256) {
        // minimumUSD
        uint256 minimumUSD = 50 * 10**18;
        uint256 price = getPrice();
        uint256 precision = 1 * 10**18;
        return (minimumUSD * precision) / price;
    }
     
    modifier onlyOwner { 
        require(msg.sender == owner, "This operation can be done only by a contract owner"); // first check this condition, ... 
        _;  // ..., if true execute the rest of the code where the modifier is used; 
    } 
     
    function withdraw() payable onlyOwner public { 
        // only owner of the contract can withdraw 
        // require(owner == msg.sender); --> replaced by the onlyOwner modifier; 
        // transfer all money from this (address of a caller) to the sender; 
        msg.sender.transfer(address(this).balance); 
         
        // once withdraw function is called, reset all funders balances (to zero) 
        // for (index, condition, 'funderIndex ++' = increase by one) 
        for (uint256 funderIndex; funderIndex < funders.length; funderIndex ++) { 
            address funder = funders[funderIndex];  // create variable funder and assign an address at the given index; 
            addressToAmountFunded[funder] = 0;  // get amount funded of the funder and set it to zero; 
        } 
        funders = new address[](0);     // reset/empty the funders array; 
    } 
}