// SPDX-License-Identifier: VPL
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@fxportal/contracts/tunnel/FxBaseChildTunnel.sol";

contract TheIndexDao is FxBaseChildTunnel, Ownable {
	
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

	constructor(
		address daoToken_, address _fxChild
	) FxBaseChildTunnel(_fxChild) {
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

	function _suggestNewCollection(address derivToken) private {
		require(!_hasAlreadyBeenSuggested[derivToken], "Token already suggested!");
		require(_isContract(derivToken), "Not a valid address");
		_auditPendingCollections.push(derivToken);
		_hasAlreadyBeenSuggested[derivToken] = true;
	}

	function _isContract(address token) internal returns (bool) {
		uint32 size;
		assembly {
			size := extcodesize(token)
		}
		return size > 0;
	}

	function voteForNewCollection(address collection, bool accept) external {
		require(canVoteOn(msg.sender, collection), "Aready voted!");
		if(accept) _likesForToken[collection] += votingPowerOf(msg.sender);
		else _dislikesForToken[collection] += votingPowerOf(msg.sender);
		setCantLongerVoteOn(msg.sender, collection);
	}

	function canVoteOn(address voter, address collection) 
		public
		view 
		returns (bool) 
	{
		return !_hasAlreadyVotedFor[
			keccak256(abi.encodePacked(voter, collection))
		];
	}

	function votingPowerOf(address voter) public view returns (uint256) {
		return IERC20(_daoToken).balanceOf(voter);
	}

	function setCantLongerVoteOn(address voter, address collection) internal {
		_hasAlreadyVotedFor[
			keccak256(abi.encodePacked(voter, collection))
		] = true;
	}
	
	function daoToken() public view returns (address) {
		return _daoToken;
	}
}

