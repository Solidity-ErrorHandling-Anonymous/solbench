// SPDX-License-Identifier: MIT
// Every.finance Contracts
pragma solidity ^0.8.4;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/AccessControlEnumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "../libraries/PendingRequest.sol";
import "../interfaces/IMetadata.sol";

/**
 * @dev Implementation of the investor's proof token {ERC721}.
 * We distinguish between deposit proof token and withdrawal proof token.
 * The investor receives the deposit/withdrawal proof token when he makes his deposit/withdrawal
 * request, waiting to be validated by the manager.
 */

contract Proof is ERC721Enumerable, Ownable, AccessControlEnumerable {
	using Strings for uint256;
	using PendingRequest for PendingRequestData;

	bytes32 public constant INVESTMENT = keccak256("INVESTMENT");
	uint256 public constant TOLERANCE_MAX = 1000; // To handel rounding errors
	uint256 public tolerance;
	uint8 public immutable id;
	bool public isOnChainMetadata;
	string public baseURI;
	address public investment;
	uint256 public totalAmount;
	mapping(uint256 => PendingRequestData) public pendingRequests;
	mapping(uint256 => uint256) public pendingIdIndex;
	mapping(address => uint256) public totalAmountPerAsset;
	uint256[] public pendingIds;
	IMetadata public metadata;

	event UpdateInvestment(address indexed investment_);
	event UpdateMetadata(address indexed metadata_);
	event UpdateBaseURI(string baseURI_);
	event UpdateTolerance(uint256 tolerance_);
	event UpdateIsOnChainMetadata(bool isOnChainMetadata_);
	event Mint(address indexed account_, uint256 tokenId_, uint256 amount_);
	event Burn(uint256 tokenId_);

	constructor(
		string memory name_,
		string memory symbol_,
		uint8 id_,
		address admin_
	) ERC721(name_, symbol_) {
		require(id_ <= 1, "Every.finance: out of range");
		require(admin_ != address(0), "Every.finance: zero address");
		id = id_;
		_setupRole(DEFAULT_ADMIN_ROLE, admin_);
	}

	/**
	 * @dev get the size of array pendingIds.
	 */
	function getPendingIdsSize() public view returns (uint256) {
		return pendingIds.length;
	}

	/**
	 * @dev Update investment.
	 * @param investment_.
	 * Emits an {UpdateInvestment} event indicating the updated investment `investment_`.
	 */
	function updateInvestment(
		address investment_
	) external onlyRole(DEFAULT_ADMIN_ROLE) {
		require(investment_ != address(0), "Every.finance: zero address");
		require(investment_ != investment, "Every.finance: no change");
		_revokeRole(INVESTMENT, investment);
		_grantRole(INVESTMENT, investment_);
		investment = investment_;
		emit UpdateInvestment(investment_);
	}

	/**
	 * @dev Update metadata.
	 * @param metadata_.
	 * Emits an {UpdateMetadata} event indicating the updated metadata `metadata_`.
	 */
	function updateMetadata(
		address metadata_
	) external onlyRole(DEFAULT_ADMIN_ROLE) {
		require(metadata_ != address(0), "Every.finance: zero address");
		require(metadata_ != address(metadata), "Every.finance: no change");
		metadata = IMetadata(metadata_);
		emit UpdateMetadata(metadata_);
	}

	/**
	 * @dev Update baseURI.
	 * @param uri_ new baseURI.
	 * Emits an {UpdateBaseURI} event indicating the updated baseURI `uri_`.
	 */
	function setBaseURI(
		string calldata uri_
	) external onlyRole(DEFAULT_ADMIN_ROLE) {
		baseURI = uri_;
		emit UpdateBaseURI(uri_);
	}

	/**
	 * @dev Update tolerance.
	 * @param tolerance_.
	 * Emits an {UpdateTolerance} event indicating the updated tolerance `tolerance_`.
	 */
	function updateTolerance(
		uint256 tolerance_
	) external onlyRole(DEFAULT_ADMIN_ROLE) {
		require(tolerance_ <= TOLERANCE_MAX, "Every.finance: tolerance max");
		require(tolerance_ != tolerance, "Every.finance: no change");
		tolerance = tolerance_;
		emit UpdateTolerance(tolerance_);
	}

	/**
	 * @dev Update isOnChainMetadata.
	 * @param isOnChainMetadata_.
	 * Emits an {UpdateIsOnChainMetadata} event indicating the updated isOnChainMetadata `isOnChainMetadata_`.
	 */
	function updateIsOnChainMetadata(
		bool isOnChainMetadata_
	) external onlyRole(DEFAULT_ADMIN_ROLE) {
		require(
			isOnChainMetadata != isOnChainMetadata_,
			"Every.finance: no change"
		);
		isOnChainMetadata = isOnChainMetadata_;
		emit UpdateIsOnChainMetadata(isOnChainMetadata_);
	}

	/**
	 * @dev mint a Proof token.
	 * The investor receives a proof Token when he makes
	 * a deposit/withdrawal request.
	 * @param account_ investor's address.
	 * @param asset_ asset's address.
	 * @param tokenId_  id of the token.
	 * @param amount_ amount to mint.
	 * @param minPrice_ minimum price of the yield-bearing token.
	 * @param maxPrice_ maximum price  of the yield-bearing token
	 * @param currentEventId_  id of the next manager event (process).
	 * Emits an {Mint} event with `account_`, `tokenId_`, and `amount`.
	 */
	function mint(
		address account_,
		address asset_,
		uint256 tokenId_,
		uint256 amount_,
		uint256 minPrice_,
		uint256 maxPrice_,
		uint256 currentEventId_
	) external onlyRole(INVESTMENT) {
		_safeMint(account_, tokenId_);
		pendingIds.push(tokenId_);
		pendingIdIndex[tokenId_] = pendingIds.length - 1;
		_increasePendingRequest(
			tokenId_,
			amount_,
			minPrice_,
			maxPrice_,
			currentEventId_,
			asset_
		);
		pendingRequests[tokenId_].asset = asset_;
		emit Mint(account_, tokenId_, amount_);
	}

	/**
	 * @dev increase the pending request balance of token `tokenId_` by `amount`.
	 * @param tokenId_  id of the token.
	 * @param amount_ amount to add.
	 * @param minPrice_ minimum price of the yield-bearing token.
	 * @param maxPrice_ maximum price  of the yield-bearing token
	 * @param currentEventId_  id of the next manager event (process).
	 * @param asset_ asset's address.
	 */

	function increasePendingRequest(
		uint256 tokenId_,
		uint256 amount_,
		uint256 minPrice_,
		uint256 maxPrice_,
		uint256 currentEventId_,
		address asset_
	) external onlyRole(INVESTMENT) {
		_increasePendingRequest(
			tokenId_,
			amount_,
			minPrice_,
			maxPrice_,
			currentEventId_,
			asset_
		);
	}

	/**
	 * @dev decrease the pending request balance of token `tokenId_` by `amount`.
	 * @param tokenId_  id of the token.
	 * @param amount_ amount to remove.
	 * @param currentEventId_  id of the next manager event (process).
	 * @param asset_ asset's address.
	 */
	function decreasePendingRequest(
		uint256 tokenId_,
		uint256 amount_,
		uint256 currentEventId_,
		address asset_
	) external onlyRole(INVESTMENT) {
		_decreasePendingRequest(tokenId_, amount_, currentEventId_, asset_);
	}

	/**
	 * @dev update event Id
	 * @param tokenId_  id of the token.
	 * @param currentEventId_  current event Id.
	 */
	function updateEventId(
		uint256 tokenId_,
		uint256 currentEventId_
	) external onlyRole(INVESTMENT) {
		pendingRequests[tokenId_].updateEventId(currentEventId_);
	}

	/**
	 * @dev update the locked and available pending balances before the manager validation.
	 * @param tokenId_  id of the token.
	 * @param currentEventId_  id of the next manager event (process).
	 */
	function preValidatePendingRequest(
		uint256 tokenId_,
		uint256 currentEventId_
	) external onlyRole(INVESTMENT) {
		pendingRequests[tokenId_].preValidate(currentEventId_);
	}

	/**
	 * @dev update the locked pending balance after the manager validation.
	 * @param tokenId_  id of the token.
	 * @param amount_  amount to remove from the locked pending balance.
	 * @param currentEventId_  id of the next manager event (process).
	 * @param asset_ asset's address.
	 */
	function validatePendingRequest(
		uint256 tokenId_,
		uint256 amount_,
		uint256 currentEventId_,
		address asset_
	) external onlyRole(INVESTMENT) {
		pendingRequests[tokenId_].validate(amount_, currentEventId_);
		_decreasetotalAmountPerAsset(tokenId_, amount_, asset_);
	}

	/**
	 * @dev  get tokenURI of token `tokenId`.
	 * If `isOnChainMetadata`, the token metadata is generated on chain.
	 *  Otherwise, see {IERC721Metadata-tokenURI}.
	 * @param tokenId  token id .
	 */
	function tokenURI(
		uint256 tokenId
	) public view virtual override returns (string memory) {
		_requireMinted(tokenId);
		if (isOnChainMetadata) {
			return metadata.render(tokenId);
		} else {
			string memory string_ = _baseURI();
			return
				bytes(string_).length > 0
					? string(abi.encodePacked(string_, tokenId.toString()))
					: "";
		}
	}

	/**
	 * @dev See {IERC165-supportsInterface}.
	 */
	function supportsInterface(
		bytes4 interfaceId
	)
		public
		view
		override(ERC721Enumerable, AccessControlEnumerable)
		returns (bool)
	{
		return
			ERC721Enumerable.supportsInterface(interfaceId) ||
			AccessControlEnumerable.supportsInterface(interfaceId);
	}

	/**
	 * @dev increase the pending request balance of token `tokenId_` by `amount`.
	 * This internal function is called when an investor makes a deposit/withdrawal request.
	 * @param tokenId_  id of the token.
	 * @param amount_ amount to add.
	 * @param minPrice_ minimum price of the yield-bearing token.
	 * @param maxPrice_ maximum price  of the yield-bearing token
	 * @param currentEventId_  id of the next manager event (process).
	 * @param asset_ asset's address.
	 */

	function _increasePendingRequest(
		uint256 tokenId_,
		uint256 amount_,
		uint256 minPrice_,
		uint256 maxPrice_,
		uint256 currentEventId_,
		address asset_
	) internal {
		pendingRequests[tokenId_].increase(
			amount_,
			minPrice_,
			maxPrice_,
			currentEventId_
		);
		totalAmountPerAsset[asset_] += amount_;
		if (id == 0) {
			totalAmount += amount_;
		}
	}

	/**
	 * @dev decrease the pending request balance of token `tokenId_` by `amount`.
	 * This internal function is called when an investor cancel a deposit/withdrawal request.
	 * @param tokenId_  id of the token.
	 * @param amount_ amount to remove.
	 * @param currentEventId_  id of the next manager event (process).
	 * @param asset_ asset's address.
	 */
	function _decreasePendingRequest(
		uint256 tokenId_,
		uint256 amount_,
		uint256 currentEventId_,
		address asset_
	) internal {
		pendingRequests[tokenId_].decrease(amount_, currentEventId_);
		_decreasetotalAmountPerAsset(tokenId_, amount_, asset_);
	}

	/**
	 * @dev burn token `tokenId_.
	 * a proof token is burned when its corresponding investor pending request is fully validated by the manager.
	 * @param tokenId_  id of the token.
	 * Emits a {Burn} event with `owner_` and `tokenId_ `.
	 */
	function burn(uint256 tokenId_) internal {
		_burn(tokenId_);
		_deleteId(tokenId_);
		emit Burn(tokenId_);
	}

	function _deleteId(uint256 id_) internal {
		uint256 index_ = pendingIdIndex[id_];
		uint256 lastId_ = pendingIds[pendingIds.length - 1];
		pendingIds[index_] = lastId_;
		pendingIds.pop();
		pendingIdIndex[lastId_] = index_;
		delete pendingIdIndex[id_];
		delete pendingRequests[id_];
	}

	/**
	 * @dev decrease totalAmountPerAsset at least by `amount`.
	 * This internal function decreases totalAmountPerAsset at least by `amount` when an investor cancels his
	 * deposit/withdrawal request `tokenId_` or the manager validates it.
	 * If the remaining pending request balance of `tokenId_` is lower than `tolerance`,
	 * the proof token `tokenId_` is burned and this remaining balance amount is removed also from totalAmountPerAsset.
	 * @param tokenId_  id of the token.
	 * @param amount_ amount of asset.
	 * @param asset_ asset's address.
	 */
	function _decreasetotalAmountPerAsset(
		uint256 tokenId_,
		uint256 amount_,
		address asset_
	) internal {
		uint256 amountToRemove_ = amount_;
		uint256 remainingAmount_ = pendingRequests[tokenId_].lockedAmount +
			pendingRequests[tokenId_].availableAmount;

		if (remainingAmount_ <= tolerance) {
			amountToRemove_ += remainingAmount_;
			burn(tokenId_);
		}
		require(
			totalAmountPerAsset[asset_] >= amountToRemove_,
			"Every.finance: max amount"
		);
		unchecked {
			totalAmountPerAsset[asset_] -= amountToRemove_;
		}

		if (id == 0) {
			unchecked {
				totalAmount -= amountToRemove_;
			}
		}
	}

	function _baseURI() internal view override returns (string memory) {
		return baseURI;
	}
}
