// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

contract Bank {
    address public owner;
    event Create(address owner, uint value);
    event Receive(address indexed sender, uint value);
    event Withdraw(address indexed owner, uint indexed value);
    modifier onlyOwner() {
        require(owner == msg.sender, "Only owner can call this function");
        _;
    }

    constructor() payable {
        owner = msg.sender;
        emit Create(owner, msg.value);
    }

    receive() external payable {
        emit Receive(msg.sender, msg.value);
    }

    function withdraw() external onlyOwner {
        address payable Receiver = payable(msg.sender);
        uint value = address(this).balance;
        Receiver.transfer(value);
        emit Withdraw(Receiver, value);
    }
}
