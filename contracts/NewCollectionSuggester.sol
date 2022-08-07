// SPDX-License-Identifier: VPL
pragma solidity ^0.8.0;

import "@fxportal/contracts/tunnel/FxBaseRootTunnel.sol";

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
		// TODO address verification logic
		_sendMessageToChild(abi.encode(newCollection));
	}
 
}
