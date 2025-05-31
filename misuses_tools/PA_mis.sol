/* PA misuse. Contract Proof.sol*/


	function _deleteId(uint256 id_) internal {
		uint256 index_ = pendingIdIndex[id_];
		uint256 lastId_ = pendingIds[pendingIds.length - 1];
		pendingIds[index_] = lastId_;
		pendingIds.pop();
		pendingIdIndex[lastId_] = index_;
		delete pendingIdIndex[id_];
		delete pendingRequests[id_];
	}
