// SPDX-License-Identifier: VPL
pragma solidity ^0.8.0;

/**
 * @dev this first version makes the final list immutable,
 * but it should be muttable so the community can 
 * vote to ban any derived collection.
 */
interface ITheIndexDao {

	/**
	 * @dev onlyOwner
	 */
	function setDaoToken(address tokenAddress) external;
	
	function getDerivs() external view returns (address[] memory);
	
	function getAuditPendingDerivs() external view returns (address[] memory);
	
	function suggestNewDeriv(address derivToken) external;
	
	/**
	 * @dev proportional voting power to DAO token holdings
	 */
	function voteForNewDeriv(address derivToAccept, bool accept) external;
	
	/**
	 * @dev returns (likes : uint256, dislikes : uint256)
	 */
	function getVotesForDeriv(address derivToken) external view returns (uint256, uint256);
	
	/**
	 * @dev once the voting period passed, anyone can add the new token
	 * to the official list. See 'canFinishVotingForDeriv'.
	 * NOTE I could automatically do this with chainlink keepers, so 
	 * theres no need for calling this function.
	 */
	function finishVotingForDeriv(address derivToken) external;
	
	/**
	 * @dev only true if enough time have passed
	 */
	function canFinishVotingForDeriv(address derivToken) external view returns (bool);

}
