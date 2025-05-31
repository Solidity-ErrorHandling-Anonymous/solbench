/*ECALL MISUSE EXAMPLE. Contract: 0xd2413729c24f77d77f53d3a3636e41ef65c4f0de.sol*/

function approveAndCall(address spender, uint tokens, bytes data) public returns (bool success) {
        allowed[msg.sender][spender] = tokens;
        emit Approval(msg.sender, spender, tokens);
        ApproveAndCallFallBack(spender).receiveApproval(msg.sender, tokens, this, data);
        return true;
}
