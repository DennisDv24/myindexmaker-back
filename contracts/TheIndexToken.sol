// SPDX-License-Identifier: VPL
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract TheIndexToken is ERC20 {

	constructor(uint256 initialSupply) ERC20("TheIndexToken", "TIT"){
		_mint(msg.sender, initialSupply);
	}

}
