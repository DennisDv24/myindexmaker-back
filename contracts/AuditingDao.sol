// SPDX-License-Identifier: VPL
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
import "@openzeppelin/contracts/utils/introspection/IERC165.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@fxportal/contracts/tunnel/FxBaseChildTunnel.sol";
import "@openzeppelin/contracts/governance/utils/IVotes.sol";

contract AuditingDao is FxBaseChildTunnel, Ownable {
	
	IVotes public immutable daoToken;
	address private _daoIndex;
	
	address[] private _auditPendingCollections;
	mapping (address => uint256) private _votationStartForCollection;
	
	mapping (address => bool) private _hasAlreadyBeenSuggested;
	
	mapping (address => uint256) private _votesFor;
	mapping (address => uint256) private _votesAgainst;
	
	/**
	 * @dev the key is a keccak256 encoding of voter and token address
	 */
	mapping (bytes32 => bool) private _hasAlreadyVotedFor;

	constructor(
		IVotes _daoToken, address _fxChild
	) FxBaseChildTunnel(_fxChild) {
		daoToken = _daoToken;	
	}
	
	function getAuditPendingDerivedCollections() 
		external 
		view 
		returns (address[] memory)
	{
		return _auditPendingCollections;
	}
	
	/**
	 * @dev FxBaseChildTunnel abstract function implementation
	 */
	function _processMessageFromRoot(
		uint256 stateId, address sender, bytes memory message
	) internal virtual override {
		_suggestNewCollection(abi.decode(message, (address)));
	}

	function suggestNewCollection(address derivToken) public onlyOwner {
		_suggestNewCollection(derivToken);
	}

	// TODO it will use the propose governor function
	function _suggestNewCollection(address derivToken) private {
		require(!_hasAlreadyBeenSuggested[derivToken], "Token already suggested!");
		_auditPendingCollections.push(derivToken);
		_votationStartForCollection[derivToken] = block.number;
		_hasAlreadyBeenSuggested[derivToken] = true;
	}

	function submitAuditForCollection(address collection, bool accept) external {
		//require(canVote(msg.sender, collection), "Aready voted!");
		if(accept) _votesFor[collection] += daoToken.getPastVotes(
			msg.sender, _votationStartForCollection[collection]
		);
		else _votesAgainst[collection] += daoToken.getPastVotes(
			msg.sender, _votationStartForCollection[collection]
		);
		//setCantLongerVoteOn(msg.sender, collection); 
		//How do i manage it with IVotes.sol?
	}
	/*
	function canVote(address voter, address collection) 
		public
		view 
		returns (bool) 
	{
		return !_hasAlreadyVotedFor[
			keccak256(abi.encodePacked(voter, collection))
		] && votingPowerOf(voter) > 0;
	}

	function votingPowerOf(address voter) public view returns (uint256) {
		return IERC20(_daoToken).balanceOf(voter);
	}

	function setCantLongerVoteOn(address voter, address collection) internal {
		_hasAlreadyVotedFor[
			keccak256(abi.encodePacked(voter, collection))
		] = true;
	}
	*/

	// TODO If IVotes is public immutable do I need this function?
	/*
	function daoToken() public view returns (address) {
		return address(daoToken);
	}
	*/
	
	/*
	function getVotesFor(address collection) 
		public 
		view 
		returns (uint256, uint256) 
	{
		return (_votesFor[collection], _votesAgainst[collection]);
	}

	function setTheIndexDao(address daoAddress) public onlyOwner {
		_daoIndex = daoAddress;	
	}

	function theIndexDao() public view returns (address) {
		return _daoIndex;
	}
	*/

}

