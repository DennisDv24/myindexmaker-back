// SPDX-License-Identifier: VPL
pragma solidity ^0.8.0;

import "@fxportal/contracts/tunnel/FxBaseRootTunnel.sol";
import "@openzeppelin/contracts/utils/introspection/IERC165.sol";

contract NewCollectionSuggester is FxBaseRootTunnel {

    constructor(
		address _checkpointManager, address _fxRoot
	) FxBaseRootTunnel(_checkpointManager, _fxRoot) { }

    function _processMessageFromChild(bytes memory message) 
		internal 
		virtual
		override
	{ }

	function suggestNewCollection(address newCollection) public {
		require(isERC721(newCollection), "Your token must implement ERC165");
		_sendMessageToChild(abi.encode(newCollection));
	}
	
	function isERC721(address tokenToCheck) public view returns (bool) {
		return IERC165(tokenToCheck).supportsInterface(0x80ac58cd);
	}
}
