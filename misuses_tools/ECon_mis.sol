/* Econ misuse. contract: 0xd2d660055fecf35b66e8e1da82c3aec55a6d2c51.sol */

   function acceptOwnership() public {
        Owner newOwner = new Owner();

        require(msg.sender == newOwner);
        emit OwnerUpdate(owner, newOwner);
        owner = newOwner;
        newOwner = address(0);
    }
}
