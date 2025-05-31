/* AA misuse. Contract: braw.sol */

function shopDrop(address _toAddress, uint256 _amount)
        external
        onlyRole(EXTERNAL_CONTRACT_ROLE)
    {
        uint256[] memory ids = new uint256[];
        uint256[] memory amounts = new uint256[];
        requestNonce++;
        uint256 baseRandomness = pseudorandom(_toAddress);
        for (uint256 i = 0; i < _amount; i++) {
            uint256 randomness = (baseRandomness / ((i + 1) * 10));
            uint256 chance = (randomness % 10000) + 1; // 1 - 10000
            for (uint256 j = 0; j < rarities.length; j++) {
                if (chance < rarities[j]) {
                    ids[i] = shopDropItemIds[j];
                    break;
                }
            }
            amounts[i] = 1;
        }
        _mintBatch(_toAddress, ids, amounts, "");
        emit ShopDrop(_toAddress, ids, amounts);
    }
