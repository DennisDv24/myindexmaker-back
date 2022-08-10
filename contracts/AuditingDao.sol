// SPDX-License-Identifier: VPL
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/introspection/IERC165.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@fxportal/contracts/tunnel/FxBaseChildTunnel.sol";

contract AuditingDao is FxBaseChildTunnel, Ownable {
	
	address private _daoToken;
	address private _daoIndex;

	address[] private _auditPendingCollections;
	
	mapping (address => bool) private _hasAlreadyBeenSuggested;
	
	mapping (address => uint256) private _votesFor;
	mapping (address => uint256) private _votesAgainst;
	
	/**
	 * @dev the key is a keccak256 encoding of voter and token address
	 */
	mapping (bytes32 => bool) private _hasAlreadyVotedFor;

	constructor(
		address daoToken_, address _fxChild
	) FxBaseChildTunnel(_fxChild) {
		_daoToken = daoToken_;	
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
		require(isERC721(derivToken), "Not a valid address");
		_auditPendingCollections.push(derivToken);
		_hasAlreadyBeenSuggested[derivToken] = true;
	}

	function submitAuditForCollection(address collection, bool accept) external {
		require(canVote(msg.sender, collection), "Aready voted!");
		if(accept) _votesFor[collection] += votingPowerOf(msg.sender);
		else _votesAgainst[collection] += votingPowerOf(msg.sender);
		setCantLongerVoteOn(msg.sender, collection);
	}

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
	
	function daoToken() public view returns (address) {
		return _daoToken;
	}

	function isERC721(address tokenToCheck) public view returns (bool) {
		return IERC165(tokenToCheck).supportsInterface(0x80ac58cd);
	}
	
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

}

