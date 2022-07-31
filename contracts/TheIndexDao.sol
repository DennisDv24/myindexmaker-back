// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract TheIndexDao is Ownable {
	
	address private _daoToken;

	address[] private _derivedCollections;
	address[] private _auditPendingCollections;
	
	mapping (address => bool) private _hasAlreadyBeenSuggested;
	

	mapping (address => uint256) private _likesForToken;
	mapping (address => uint256) private _dislikesForToken;
	
	
	/**
	 * @dev the key is a keccak256 encoding of voter and token address
	 */
	mapping (bytes32 => bool) private _hasAlreadyVotedFor;

	constructor(address daoToken_) {
		_daoToken = daoToken_;	
	}

	function getDerivedCollections() external view returns (address[] memory) {
		return _derivedCollections;
	}
	
	function getAuditPendingDerivedCollections() 
		external 
		view 
		returns (address[] memory)
	{
		return _auditPendingCollections;
	}

	/**
     * @dev for now you can only suggest a collection once
	 */
	function suggestNewCollection(address derivToken) external {
		if(_hasAlreadyBeenSuggested[derivToken]) return;
		_auditPendingCollections.push(derivToken);
		_hasAlreadyBeenSuggested[derivToken] = true;
	} 

	function voteForNewCollection(address tokenToVote, bool accept) external {
		require(canVoteOn(msg.sender, tokenToVote), "Aready voted!");
		(uint256 likes, uint256 dislikes) = getVotesForDeriv(tokenToVote);
		if(accept) _likesForToken[tokenToVote] += votingPowerOf(msg.sender);
		else _dislikesForToken[tokenToVote] += votingPowerOf(msg.sender);
		setCantLongerVoteOn(msg.sender, tokenToVote);
	}

	function canVoteOn(address voter, address tokenToVote) 
		public
		view 
		returns (bool) 
	{
		return !_hasAlreadyVotedFor[
			keccak256(abi.encodePacked(voter, tokenToVote))
		];
	}

	function setCantLongerVoteOn(address voter, address tokenToVote) internal {
		_hasAlreadyVotedFor[
			keccak256(abi.encodePacked(voter, tokenToVote))
		] = true;
	}

	function getVotesForDeriv(address derivToken) 
		public
		view
		returns (uint256, uint256) 
	{
		return (_likesForToken[derivToken], _dislikesForToken[derivToken]);
	}

	function votingPowerOf(address voter) public view returns (uint256) {
		return IERC20(_daoToken).balanceOf(voter);
	}

}
