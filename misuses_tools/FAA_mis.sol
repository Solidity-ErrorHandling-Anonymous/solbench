/* FAA_mis.sol. Contract: 0xd29b239328ce77775ee518bbab99d40dbfe3cf2e.sol */

    function mint(address _to, uint256 _amount) onlyAdminer public returns (bool) {
        totalSupply = totalSupply.add(_amount);
        balances[_to] = balances[_to].sub(_amount);
        emit Mint(_to, _amount);
        emit Transfer(address(0), _to, _amount);
        return true;
    }
