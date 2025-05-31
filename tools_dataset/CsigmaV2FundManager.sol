// SPDX-License-Identifier: BUSL-1.1
// @author cSigma Finance Inc., a Delaware company, for its Real World Credit tokenization protocol

pragma solidity 0.8.9;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/utils/SafeERC20Upgradeable.sol";
import "../interfaces/ICsigmaV1.sol";
import "./CsigmaV2Pool.sol";

error V1PoolIsNotActive(string _poolId);
error InvalidV1Pool(string _poolId);
error InvalidAllocation(uint256 _allocation);
error InvalidV1Amount(uint256 _v1Amount);
error InvalidAmount(uint256 _v2Amount, uint256 _v1Amount);
error DuplicatePool(string _poolId);

/// @title CsigmaV2FundManager
/// @notice This contract manages the fund deployment and claim process for the cSigma V2 Pool Managers
contract CsigmaV2FundManager is
    Initializable,
    AccessControlUpgradeable,
    UUPSUpgradeable,
    PausableUpgradeable
{
    address public factory;
    address public pool;
    address public poolToken;
    address public diamondV1;
    uint16 public totalAllocation;
    string public fundManagerLenderId;
    PoolInfo[] public v1Pools;
    mapping (string => bool) private _isUsed;

    /// @notice PoolInfo struct to store the V1 pool information
    /// @param v1PoolId The V1 pool ID
    /// @param allocation The allocation percentage of the pool
    struct PoolInfo {
        string v1PoolId;
        uint16 allocation;
    }

    /// @notice Claim struct to store the claim information
    /// @param request The V1 request
    /// @param sigR The R value of the signature
    /// @param sigS The S value of the signature
    /// @param sigV The V value of the signature
    struct Claim {
        ICsigmaV1.Request request;
        bytes32 sigR;
        bytes32 sigS;
        uint8 sigV;
    }

    /// @notice Disburse struct to store the disburse information
    /// @param v1PoolIndex The index of the V1 pool
    /// @param amount The amount to disburse
    struct Disburse {
        uint256 v1PoolIndex;
        uint256 amount;
    }

    event AdminTransferred(address _oldOwner, address _newOwner);
    event V1PoolAdded(address indexed _executor, uint16 _allocation, string _v1PoolId);
    event V1PoolRemoved(address indexed _executor, uint16 _allocation, string _v1PoolId);
    event V1PoolAllocationUpdated(
        address indexed _executor,
        uint16 _prevAllocation,
        uint16 _newAllocation,
        string _v1PoolId
    );
    event FundDeployed(address indexed _executor, uint256 _amount);
    event FundClaimed(address indexed _executor, uint256 _amount);
    event EmergencyWithdraw(address _token, address _to, uint256 _amount);

    modifier notZeroAddress(address _account) {
        require(_account != address(0), "address cannot be zero");
        _;
    }

    modifier onlyPoolManager() {
        if(_msgSender() != CsigmaV2Pool(pool).poolManager()) {
            revert AccessDenied(_msgSender());
        }
        _;
    }

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    /// @notice Initializes the contract with the required parameters
    /// @param _poolToken The address of the pool token
    /// @param _diamondV1 The address of the V1 diamond
    /// @param _lenderId The lender ID of the fund manager
    /// @param _pool The address of the V2 pool
    function initialize(
        address _poolToken,
        address _diamondV1,
        string calldata _lenderId,
        address _pool
    )
        public
        initializer
    {
        __AccessControl_init();
        __UUPSUpgradeable_init();
        __Pausable_init();

        _grantRole(DEFAULT_ADMIN_ROLE, _msgSender());
        factory = _msgSender();
        poolToken = _poolToken;
        diamondV1 = _diamondV1;
        fundManagerLenderId = _lenderId;
        pool = _pool;
        SafeERC20Upgradeable.forceApprove(IERC20Upgradeable(_poolToken), _diamondV1, type(uint256).max);
    }

    /// @notice Returns the total number of V1 pools to which the funds are deployed
    function totalV1Pools() external view returns (uint256) {
        return v1Pools.length;
    }

    /// @notice Returns the total assets under management
    function totalAssets() public view virtual returns (uint256) {
        return (IERC20Upgradeable(poolToken).balanceOf(address(this)) + ICsigmaV1(diamondV1).getTokenBalance(fundManagerLenderId, poolToken));
    }

    /// @notice Adds a new V1 pool to the fund manager
    /// @dev Only the pool manager can call this function
    /// @param _v1PoolId The V1 pool ID
    /// @param _allocation The allocation percentage of the pool
    function addPool(string calldata _v1PoolId, uint16 _allocation) external onlyPoolManager whenNotPaused {
        if(_isUsed[_v1PoolId]) revert DuplicatePool(_v1PoolId);
        if(ICsigmaV1(diamondV1).getCreditPoolStatus(_v1PoolId) != ICsigmaV1.CreditPoolStatus.ACTIVE) {
            revert V1PoolIsNotActive(_v1PoolId);
        }
        if(ICsigmaV1(diamondV1).getPoolToken(_v1PoolId) != poolToken) {
            revert InvalidV1Pool(_v1PoolId);
        }
        if(_allocation + totalAllocation > 10000) {
            revert InvalidAllocation(_allocation);
        }
        v1Pools.push(PoolInfo(_v1PoolId, _allocation));
        totalAllocation += _allocation;
        _isUsed[_v1PoolId] = true;
        emit V1PoolAdded(_msgSender(), _allocation, _v1PoolId); 
    }

    /// @notice Removes a V1 pool from the fund manager
    /// @dev Only the pool manager can call this function
    /// @param _index The index of the V1 pool
    function removePool(uint256 _index) external onlyPoolManager whenNotPaused {
        uint256 _lastIndex = v1Pools.length - 1;
        PoolInfo memory _pool = v1Pools[_index];
        if(_index != _lastIndex) {
            v1Pools[_index] = v1Pools[_lastIndex];
        }
        v1Pools.pop();
        _isUsed[_pool.v1PoolId] = false;
        totalAllocation -= _pool.allocation;
        emit V1PoolRemoved(_msgSender(), _pool.allocation, _pool.v1PoolId);
    }

    /// @notice Updates the allocation of a V1 pool
    /// @dev Only the pool manager can call this function
    /// @param _index The index of the V1 pool
    /// @param _allocation The new allocation percentage of the pool
    function updatePoolAllocation(uint256 _index, uint16 _allocation) external onlyPoolManager whenNotPaused {
        PoolInfo memory _pool = v1Pools[_index];
        if(((_allocation + totalAllocation) - _pool.allocation) > 10000) {
            revert InvalidAllocation(_allocation);
        }
        v1Pools[_index].allocation = _allocation; 
        totalAllocation = (_allocation + totalAllocation) - _pool.allocation;
        emit V1PoolAllocationUpdated(_msgSender(), _pool.allocation, _allocation, _pool.v1PoolId);
    }

    /// @notice Deploys the funds to the V1 pools
    /// @dev Only the pool manager can call this function
    function deployFunds() external onlyPoolManager whenNotPaused {
        if(totalAllocation != 10000) revert InvalidAllocation(totalAllocation);
        uint256 _bal = IERC20Upgradeable(poolToken).balanceOf(address(this));
        ICsigmaV1(diamondV1).deposit(fundManagerLenderId, poolToken, _bal);
        uint256 _amount;
        uint256 _deployed;
        for(uint i; i < v1Pools.length; i++) {
            _amount = (_bal * v1Pools[i].allocation) / 10000;
            _deployed += _amount;
            ICsigmaV1(diamondV1).invest(fundManagerLenderId, v1Pools[i].v1PoolId, _amount);
        }
        CsigmaV2Pool(pool).updateAssetUnderManagement(CsigmaV2Pool(pool).assetUnderManagement() + _deployed);
        emit FundDeployed(_msgSender(), _bal);
    }

    /// @notice Claims the funds from the V1 pools
    /// @dev Only the pool manager can call this function
    /// @param _claim The claim information
    function claimFunds(Claim[] calldata _claim) external onlyPoolManager whenNotPaused {
        uint256 _initial = ICsigmaV1(diamondV1).getTokenBalance(fundManagerLenderId, poolToken);
        for(uint i; i < _claim.length; i++) {
            ICsigmaV1(diamondV1).withdrawPoolPaymentIntoVault(
                _claim[i].request,
                _claim[i].sigR,
                _claim[i].sigS,
                _claim[i].sigV
            );
        }
        uint256 _recouped = ICsigmaV1(diamondV1).getTokenBalance(fundManagerLenderId, poolToken);
        CsigmaV2Pool(pool).updateAssetUnderManagement(CsigmaV2Pool(pool).assetUnderManagement() - (_recouped - _initial));
        ICsigmaV1(diamondV1).withdrawRequest(fundManagerLenderId, poolToken, _recouped);
        emit FundClaimed(_msgSender(), _recouped);
    }
    
    /// @notice Sends the funds to the V2 pool reserve
    /// @dev Only the pool manager can call this function
    /// @param _v2Amount The amount to send to the V2 pool reserve
    function sendToV2Reserve(uint256 _v2Amount) external onlyPoolManager whenNotPaused {
        SafeERC20Upgradeable.safeTransfer(IERC20Upgradeable(poolToken), pool, _v2Amount);
    }

    /// @notice Pauses the contract
    /// @dev Only the admin can call this function
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    /// @notice Unpauses the contract
    /// @dev Only the admin can call this function
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }

    /// @notice Withdraws the funds from the contract
    /// @dev Only the admin can call this function
    /// @param _token The address of the token
    /// @param _to The address to which the funds are withdrawn
    /// @param _amount The amount to withdraw
    function emergencyWithdraw(address _token, address _to, uint256 _amount) external onlyRole(DEFAULT_ADMIN_ROLE) {
        SafeERC20Upgradeable.safeTransfer(IERC20Upgradeable(_token), _to, _amount);
        emit EmergencyWithdraw(_token, _to, _amount);
    }

    /// @notice Transfers the admin role to a new address
    /// @param _newOwner The address of the new admin
    function transferAdmin(address _newOwner) public
    {
        grantRole(DEFAULT_ADMIN_ROLE, _newOwner);
        revokeRole(DEFAULT_ADMIN_ROLE, _msgSender());
        emit AdminTransferred(_msgSender(), _newOwner);
    }    

    /// @notice Grants the given role to the account
    /// @param role The role to grant
    /// @param _account The address to which the role is granted
    function grantRole(bytes32 role, address _account)
        public
        virtual
        override
        onlyRole(getRoleAdmin(role))
        notZeroAddress(_account)
        whenNotPaused
    {
        _grantRole(role, _account);
    }

    /// @notice Revokes the given role from the account
    /// @param role The role to revoke
    /// @param _account The address from which the role is revoked
    function revokeRole(bytes32 role, address _account)
        public
        override
        onlyRole(getRoleAdmin(role))        
        notZeroAddress(_account)        
        whenNotPaused
    {
        _revokeRole(role, _account);
    }

    /// @notice Upgrades the contract to a new implementation
    /// @dev Only the admin can call this function
    /// @param _newImplementation The address of the new implementation
    function _authorizeUpgrade(address _newImplementation)
        internal
        override
        onlyRole(DEFAULT_ADMIN_ROLE)
    {}
}
