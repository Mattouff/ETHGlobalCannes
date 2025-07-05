// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// Import interfaces directement depuis chainlink-brownie-contracts
import {AggregatorV3Interface} from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";
import {AutomationCompatibleInterface} from "@chainlink/contracts/src/v0.8/automation/AutomationCompatible.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title IntentFi
 * @notice Smart contract for autonomous financial intent scheduling with cross-chain execution
 * @dev Integrates Chainlink Price Feeds and Automation for automated intent execution
 */
contract IntentFi is Ownable, AutomationCompatibleInterface {
    // Custom errors
    error NotEnoughBalance(uint256 currentBalance, uint256 required);
    error NothingToWithdraw();
    error FailedToWithdrawEth(address owner, address target, uint256 value);
    error DestinationChainNotAllowed(uint64 destinationChainSelector);
    error InvalidReceiverAddress();
    error IntentNotFound(uint256 intentId);
    error IntentAlreadyExecuted(uint256 intentId);
    error UnauthorizedIntentExecution(address caller, address intentOwner);

    // Events
    event IntentCreated(
        uint256 indexed intentId,
        address indexed owner,
        IntentType intentType,
        int256 triggerPrice,
        uint256 amount,
        uint64 destinationChain,
        address destinationReceiver
    );
    
    event IntentExecuted(
        uint256 indexed intentId,
        uint64 destinationChainSelector,
        address receiver,
        uint256 amount
    );
    
    event CrossChainMessageSent(
        uint256 indexed intentId,
        uint64 indexed destinationChainSelector,
        address receiver,
        uint256 amount
    );

    // Enums
    enum IntentType {
        SEND_IF_PRICE_ABOVE,
        SEND_IF_PRICE_BELOW,
        CROSS_CHAIN_SWAP,
        AUTOMATED_DCA
    }

    enum IntentStatus {
        ACTIVE,
        EXECUTED,
        CANCELLED
    }

    // Structs
    struct Intent {
        uint256 id;
        address owner;
        IntentType intentType;
        int256 triggerPrice; // Price trigger in USD (8 decimals)
        uint256 amount; // Amount to transfer
        address tokenAddress; // Token to transfer (address(0) for ETH)
        uint64 destinationChainSelector;
        address destinationReceiver;
        IntentStatus status;
        uint256 createdAt;
        uint256 lastChecked;
    }

    // State variables
    AggregatorV3Interface private s_priceFeed;
    
    uint256 private s_nextIntentId = 1;
    mapping(uint256 => Intent) public intents;
    mapping(address => uint256[]) public userIntents;
    mapping(uint64 => bool) public allowlistedDestinationChains;
    
    uint256[] private activeIntentIds;
    uint256 public constant PRICE_FEED_HEARTBEAT = 3600; // 1 hour
    uint256 public constant MAX_INTENTS_PER_CHECK = 10;

    // CCIP Integration (placeholder for future implementation)
    address public ccipRouterAddress;
    
    modifier onlyAllowlistedDestinationChain(uint64 _destinationChainSelector) {
        if (!allowlistedDestinationChains[_destinationChainSelector])
            revert DestinationChainNotAllowed(_destinationChainSelector);
        _;
    }

    modifier validReceiver(address _receiver) {
        if (_receiver == address(0)) revert InvalidReceiverAddress();
        _;
    }

    /**
     * @notice Constructor initializes the contract with Chainlink components
     * @param _priceFeed The address of the ETH/USD price feed contract
     * @param _ccipRouter The address of the CCIP router contract (for future use)
     */
    constructor(
        address _priceFeed,
        address _ccipRouter
    ) Ownable(msg.sender) {
        s_priceFeed = AggregatorV3Interface(_priceFeed);
        ccipRouterAddress = _ccipRouter;
    }

    /**
     * @notice Create a new financial intent
     * @param _intentType The type of intent to create
     * @param _triggerPrice The price that triggers the intent execution
     * @param _amount The amount to transfer when triggered
     * @param _tokenAddress The token address (address(0) for ETH)
     * @param _destinationChainSelector The destination chain selector
     * @param _destinationReceiver The receiver address on destination chain
     */
    function createIntent(
        IntentType _intentType,
        int256 _triggerPrice,
        uint256 _amount,
        address _tokenAddress,
        uint64 _destinationChainSelector,
        address _destinationReceiver
    ) 
        external 
        payable 
        onlyAllowlistedDestinationChain(_destinationChainSelector)
        validReceiver(_destinationReceiver)
        returns (uint256 intentId)
    {
        require(_amount > 0, "Amount must be greater than 0");
        require(_triggerPrice > 0, "Trigger price must be greater than 0");

        // If transferring tokens, ensure user has approved the contract
        if (_tokenAddress != address(0)) {
            IERC20 token = IERC20(_tokenAddress);
            require(
                token.transferFrom(msg.sender, address(this), _amount),
                "Token transfer failed"
            );
        } else {
            // For ETH transfers, ensure enough ETH is sent
            require(msg.value >= _amount, "Insufficient ETH sent");
        }

        intentId = s_nextIntentId++;
        
        Intent memory newIntent = Intent({
            id: intentId,
            owner: msg.sender,
            intentType: _intentType,
            triggerPrice: _triggerPrice,
            amount: _amount,
            tokenAddress: _tokenAddress,
            destinationChainSelector: _destinationChainSelector,
            destinationReceiver: _destinationReceiver,
            status: IntentStatus.ACTIVE,
            createdAt: block.timestamp,
            lastChecked: block.timestamp
        });

        intents[intentId] = newIntent;
        userIntents[msg.sender].push(intentId);
        activeIntentIds.push(intentId);

        emit IntentCreated(
            intentId,
            msg.sender,
            _intentType,
            _triggerPrice,
            _amount,
            _destinationChainSelector,
            _destinationReceiver
        );
    }

    /**
     * @notice Chainlink Automation checkUpkeep function
     * @dev Called by Chainlink Automation to check if any intents need execution
     */
    function checkUpkeep(bytes calldata /* checkData */)
        external
        view
        override
        returns (bool upkeepNeeded, bytes memory performData)
    {
        uint256[] memory readyIntents = new uint256[](MAX_INTENTS_PER_CHECK);
        uint256 count = 0;

        // Get current price
        (, int256 currentPrice, , uint256 updatedAt, ) = s_priceFeed.latestRoundData();
        
        // Check if price data is fresh
        if (block.timestamp - updatedAt > PRICE_FEED_HEARTBEAT) {
            return (false, "");
        }

        // Check active intents
        for (uint256 i = 0; i < activeIntentIds.length && count < MAX_INTENTS_PER_CHECK; i++) {
            uint256 intentId = activeIntentIds[i];
            Intent memory intent = intents[intentId];
            
            if (intent.status == IntentStatus.ACTIVE) {
                bool shouldExecute = false;
                
                if (intent.intentType == IntentType.SEND_IF_PRICE_ABOVE) {
                    shouldExecute = currentPrice >= intent.triggerPrice;
                } else if (intent.intentType == IntentType.SEND_IF_PRICE_BELOW) {
                    shouldExecute = currentPrice <= intent.triggerPrice;
                }
                
                if (shouldExecute) {
                    readyIntents[count] = intentId;
                    count++;
                }
            }
        }

        if (count > 0) {
            // Resize array to actual count
            uint256[] memory intentsToExecute = new uint256[](count);
            for (uint256 i = 0; i < count; i++) {
                intentsToExecute[i] = readyIntents[i];
            }
            
            upkeepNeeded = true;
            performData = abi.encode(intentsToExecute);
        }
    }

    /**
     * @notice Chainlink Automation performUpkeep function
     * @dev Called by Chainlink Automation to execute ready intents
     */
    function performUpkeep(bytes calldata performData) external override {
        uint256[] memory intentIds = abi.decode(performData, (uint256[]));
        
        for (uint256 i = 0; i < intentIds.length; i++) {
            _executeIntent(intentIds[i]);
        }
    }

    /**
     * @notice Execute a specific intent manually (for testing or emergency)
     * @param _intentId The ID of the intent to execute
     */
    function executeIntent(uint256 _intentId) external {
        Intent storage intent = intents[_intentId];
        
        if (intent.id == 0) revert IntentNotFound(_intentId);
        if (intent.status != IntentStatus.ACTIVE) revert IntentAlreadyExecuted(_intentId);
        if (intent.owner != msg.sender && msg.sender != owner()) {
            revert UnauthorizedIntentExecution(msg.sender, intent.owner);
        }

        _executeIntent(_intentId);
    }

    /**
     * @notice Internal function to execute an intent
     * @param _intentId The ID of the intent to execute
     */
    function _executeIntent(uint256 _intentId) internal {
        Intent storage intent = intents[_intentId];
        
        if (intent.status != IntentStatus.ACTIVE) return;
        
        intent.status = IntentStatus.EXECUTED;
        
        // Remove from active intents array
        _removeFromActiveIntents(_intentId);
        
        // For now, simulate cross-chain sending (CCIP integration will be added later)
        _simulateCrossChainSend(intent);

        emit IntentExecuted(
            _intentId,
            intent.destinationChainSelector,
            intent.destinationReceiver,
            intent.amount
        );
    }

    /**
     * @notice Simulate cross-chain sending (placeholder for CCIP integration)
     * @dev This function will be replaced with actual CCIP sending functionality
     * @param intent The intent to execute
     */
    function _simulateCrossChainSend(Intent memory intent) internal virtual {
        // For now, we'll keep the funds in the contract
        // In the full CCIP implementation, this would send via ccipSend()
        
        emit CrossChainMessageSent(
            intent.id,
            intent.destinationChainSelector,
            intent.destinationReceiver,
            intent.amount
        );
    }

    /**
     * @notice Remove an intent ID from the active intents array
     * @param _intentId The intent ID to remove
     */
    function _removeFromActiveIntents(uint256 _intentId) internal {
        for (uint256 i = 0; i < activeIntentIds.length; i++) {
            if (activeIntentIds[i] == _intentId) {
                activeIntentIds[i] = activeIntentIds[activeIntentIds.length - 1];
                activeIntentIds.pop();
                break;
            }
        }
    }

    /**
     * @notice Cancel an active intent
     * @param _intentId The ID of the intent to cancel
     */
    function cancelIntent(uint256 _intentId) external {
        Intent storage intent = intents[_intentId];
        
        if (intent.id == 0) revert IntentNotFound(_intentId);
        if (intent.owner != msg.sender) revert UnauthorizedIntentExecution(msg.sender, intent.owner);
        if (intent.status != IntentStatus.ACTIVE) revert IntentAlreadyExecuted(_intentId);
        
        intent.status = IntentStatus.CANCELLED;
        _removeFromActiveIntents(_intentId);
        
        // Refund the locked amount
        if (intent.tokenAddress == address(0)) {
            payable(intent.owner).transfer(intent.amount);
        } else {
            require(IERC20(intent.tokenAddress).transfer(intent.owner, intent.amount), "Refund failed");
        }
    }

    // Admin functions
    function allowlistDestinationChain(uint64 _destinationChainSelector, bool allowed) external onlyOwner {
        allowlistedDestinationChains[_destinationChainSelector] = allowed;
    }

    function updateCCIPRouter(address _newRouter) external onlyOwner {
        ccipRouterAddress = _newRouter;
    }

    function updatePriceFeed(address _newPriceFeed) external onlyOwner {
        s_priceFeed = AggregatorV3Interface(_newPriceFeed);
    }

    // View functions
    function getUserIntents(address _user) external view returns (uint256[] memory) {
        return userIntents[_user];
    }
    
    function getActiveIntents() external view returns (uint256[] memory) {
        return activeIntentIds;
    }
    
    function getCurrentPrice() public view returns (int256) {
        (, int256 price, , , ) = s_priceFeed.latestRoundData();
        return price;
    }

    function getIntentDetails(uint256 _intentId) external view returns (Intent memory) {
        return intents[_intentId];
    }

    // Withdraw functions (for admin use and emergency)
    function withdraw(address _beneficiary) public onlyOwner {
        uint256 amount = address(this).balance;
        if (amount == 0) revert NothingToWithdraw();
        (bool sent, ) = _beneficiary.call{value: amount}("");
        if (!sent) revert FailedToWithdrawEth(msg.sender, _beneficiary, amount);
    }

    function withdrawToken(address _beneficiary, address _token) public onlyOwner {
        uint256 amount = IERC20(_token).balanceOf(address(this));
        if (amount == 0) revert NothingToWithdraw();
        require(IERC20(_token).transfer(_beneficiary, amount), "Withdrawal failed");
    }

    // Receive function to accept ETH
    receive() external payable {}
}
