// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {IntentFiCCIP} from "./IntentFiCCIP.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title IntentFiAdvanced
 * @notice Advanced version of IntentFi with DCA, multi-trigger, and complex strategies
 * @dev Extends IntentFiCCIP with advanced financial instruments
 */
contract IntentFiAdvanced is IntentFiCCIP, ReentrancyGuard {
    
    // Advanced Intent Types
    enum AdvancedIntentType {
        DCA_BUY,                    // Dollar Cost Averaging - Buy
        DCA_SELL,                   // Dollar Cost Averaging - Sell
        RANGE_TRADING,              // Trade within a price range
        STOP_LOSS,                  // Stop loss order
        TAKE_PROFIT,                // Take profit order
        MULTI_TRIGGER,              // Multiple conditions
        TIME_BASED,                 // Time-based execution
        YIELD_FARMING,              // Yield farming strategy
        REBALANCING                 // Portfolio rebalancing
    }

    // Advanced Intent Structure
    struct AdvancedIntent {
        uint256 id;
        address user;
        AdvancedIntentType advancedType;
        int256 triggerPrice;
        int256 upperBound;          // For range trading
        int256 lowerBound;          // For range trading
        uint256 amount;
        uint256 frequency;          // For DCA (in seconds)
        uint256 lastExecution;      // Last execution timestamp
        uint256 maxExecutions;      // Max number of executions
        uint256 executionCount;     // Current execution count
        address tokenAddress;
        uint64 destinationChainSelector;
        address destinationReceiver;
        bool isActive;
        bytes extraData;            // Additional strategy parameters
    }

    // Strategy Parameters for different intent types
    struct DCAParams {
        uint256 investmentAmount;   // Amount to invest each period
        uint256 intervalSeconds;    // Interval between investments
        uint256 totalPeriods;       // Total number of investment periods
        address targetToken;        // Token to purchase
        uint256 slippageTolerance;  // Slippage tolerance (basis points)
    }

    struct RangeParams {
        int256 buyPrice;           // Price to buy at
        int256 sellPrice;          // Price to sell at
        uint256 tradeAmount;       // Amount to trade each time
        uint256 maxTrades;         // Maximum number of trades
    }

    struct YieldParams {
        address yieldProtocol;     // Address of yield protocol
        uint256 minYield;          // Minimum yield percentage
        uint256 stakingAmount;     // Amount to stake
        uint256 compoundFrequency; // How often to compound
    }

    // Events for advanced features
    event AdvancedIntentCreated(
        uint256 indexed id,
        address indexed user,
        AdvancedIntentType advancedType,
        uint256 amount
    );

    event DCAExecuted(
        uint256 indexed intentId,
        uint256 executionNumber,
        uint256 amount,
        int256 price
    );

    event RangeTradeExecuted(
        uint256 indexed intentId,
        bool isBuy,
        uint256 amount,
        int256 price
    );

    event YieldHarvested(
        uint256 indexed intentId,
        uint256 yield,
        address protocol
    );

    event IntentCancelled(uint256 indexed intentId);

    // State variables
    mapping(uint256 => AdvancedIntent) public advancedIntents;
    mapping(address => uint256[]) public userAdvancedIntents;
    mapping(address => bool) public supportedYieldProtocols;
    
    uint256 public nextAdvancedIntentId = 1;
    uint256 public constant MAX_SLIPPAGE = 1000; // 10% max slippage

    // Modifiers
    modifier validAdvancedIntent(uint256 _intentId) {
        require(advancedIntents[_intentId].id != 0, "Intent does not exist");
        require(advancedIntents[_intentId].isActive, "Intent is not active");
        _;
    }

    constructor(
        address _priceFeed,
        address _ccipRouter,
        address _linkToken
    ) IntentFiCCIP(_priceFeed, _ccipRouter, _linkToken) {}

    /**
     * @notice Create a DCA (Dollar Cost Averaging) intent
     * @param params DCA parameters
     * @param destinationChain Chain to send tokens to
     * @param receiver Address to receive tokens
     */
    function createDCAIntent(
        DCAParams memory params,
        uint64 destinationChain,
        address receiver
    ) external payable returns (uint256 intentId) {
        require(params.investmentAmount > 0, "Investment amount must be > 0");
        require(params.intervalSeconds >= 300, "Interval must be >= 5 minutes");
        require(params.totalPeriods > 0, "Total periods must be > 0");
        require(params.slippageTolerance <= MAX_SLIPPAGE, "Slippage too high");

        intentId = nextAdvancedIntentId++;
        
        AdvancedIntent storage intent = advancedIntents[intentId];
        intent.id = intentId;
        intent.user = msg.sender;
        intent.advancedType = AdvancedIntentType.DCA_BUY;
        intent.amount = params.investmentAmount * params.totalPeriods;
        intent.frequency = params.intervalSeconds;
        intent.maxExecutions = params.totalPeriods;
        intent.destinationChainSelector = destinationChain;
        intent.destinationReceiver = receiver;
        intent.isActive = true;
        intent.extraData = abi.encode(params);

        // Transfer total DCA amount to contract
        IERC20(params.targetToken).transferFrom(
            msg.sender,
            address(this),
            intent.amount
        );

        userAdvancedIntents[msg.sender].push(intentId);

        emit AdvancedIntentCreated(
            intentId,
            msg.sender,
            AdvancedIntentType.DCA_BUY,
            intent.amount
        );
    }

    /**
     * @notice Create a range trading intent
     * @param params Range trading parameters
     * @param destinationChain Chain to send tokens to
     * @param receiver Address to receive tokens
     */
    function createRangeIntent(
        RangeParams memory params,
        uint64 destinationChain,
        address receiver
    ) external payable returns (uint256 intentId) {
        require(params.buyPrice > 0 && params.sellPrice > params.buyPrice, "Invalid price range");
        require(params.tradeAmount > 0, "Trade amount must be > 0");
        require(params.maxTrades > 0, "Max trades must be > 0");

        intentId = nextAdvancedIntentId++;
        
        AdvancedIntent storage intent = advancedIntents[intentId];
        intent.id = intentId;
        intent.user = msg.sender;
        intent.advancedType = AdvancedIntentType.RANGE_TRADING;
        intent.lowerBound = params.buyPrice;
        intent.upperBound = params.sellPrice;
        intent.amount = params.tradeAmount * params.maxTrades;
        intent.maxExecutions = params.maxTrades;
        intent.destinationChainSelector = destinationChain;
        intent.destinationReceiver = receiver;
        intent.isActive = true;
        intent.extraData = abi.encode(params);

        userAdvancedIntents[msg.sender].push(intentId);

        emit AdvancedIntentCreated(
            intentId,
            msg.sender,
            AdvancedIntentType.RANGE_TRADING,
            intent.amount
        );
    }

    /**
     * @notice Create a yield farming intent
     * @param params Yield farming parameters
     * @param destinationChain Chain to send rewards to
     * @param receiver Address to receive rewards
     */
    function createYieldIntent(
        YieldParams memory params,
        uint64 destinationChain,
        address receiver
    ) external payable returns (uint256 intentId) {
        require(supportedYieldProtocols[params.yieldProtocol], "Unsupported yield protocol");
        require(params.stakingAmount > 0, "Staking amount must be > 0");
        require(params.minYield > 0, "Min yield must be > 0");

        intentId = nextAdvancedIntentId++;
        
        AdvancedIntent storage intent = advancedIntents[intentId];
        intent.id = intentId;
        intent.user = msg.sender;
        intent.advancedType = AdvancedIntentType.YIELD_FARMING;
        intent.amount = params.stakingAmount;
        intent.frequency = params.compoundFrequency;
        intent.destinationChainSelector = destinationChain;
        intent.destinationReceiver = receiver;
        intent.isActive = true;
        intent.extraData = abi.encode(params);

        userAdvancedIntents[msg.sender].push(intentId);

        emit AdvancedIntentCreated(
            intentId,
            msg.sender,
            AdvancedIntentType.YIELD_FARMING,
            intent.amount
        );
    }

    /**
     * @notice Execute DCA intent
     * @param intentId ID of the DCA intent to execute
     */
    function executeDCAIntent(uint256 intentId) 
        external 
        validAdvancedIntent(intentId) 
        nonReentrant 
    {
        AdvancedIntent storage intent = advancedIntents[intentId];
        require(intent.advancedType == AdvancedIntentType.DCA_BUY, "Not a DCA intent");
        require(
            block.timestamp >= intent.lastExecution + intent.frequency,
            "Too early for next execution"
        );
        require(intent.executionCount < intent.maxExecutions, "All executions completed");

        DCAParams memory params = abi.decode(intent.extraData, (DCAParams));
        int256 currentPrice = getCurrentPrice();
        
        // Calculate slippage-adjusted amount
        uint256 adjustedAmount = _calculateSlippageAmount(
            params.investmentAmount,
            params.slippageTolerance
        );

        // Execute the DCA trade
        _executeDCATrade(intent, adjustedAmount, currentPrice);

        intent.lastExecution = block.timestamp;
        intent.executionCount++;

        if (intent.executionCount >= intent.maxExecutions) {
            intent.isActive = false;
        }

        emit DCAExecuted(intentId, intent.executionCount, adjustedAmount, currentPrice);
    }

    /**
     * @notice Execute range trading intent
     * @param intentId ID of the range intent to execute
     */
    function executeRangeIntent(uint256 intentId) 
        external 
        validAdvancedIntent(intentId) 
        nonReentrant 
    {
        AdvancedIntent storage intent = advancedIntents[intentId];
        require(intent.advancedType == AdvancedIntentType.RANGE_TRADING, "Not a range intent");

        int256 currentPrice = getCurrentPrice();
        RangeParams memory params = abi.decode(intent.extraData, (RangeParams));

        bool shouldExecute = false;
        bool isBuy = false;

        if (currentPrice <= params.buyPrice) {
            shouldExecute = true;
            isBuy = true;
        } else if (currentPrice >= params.sellPrice) {
            shouldExecute = true;
            isBuy = false;
        }

        require(shouldExecute, "Price not in execution range");
        require(intent.executionCount < intent.maxExecutions, "Max trades reached");

        _executeRangeTrade(intent, params.tradeAmount, isBuy);

        intent.executionCount++;
        if (intent.executionCount >= intent.maxExecutions) {
            intent.isActive = false;
        }

        emit RangeTradeExecuted(intentId, isBuy, params.tradeAmount, currentPrice);
    }

    /**
     * @notice Calculate slippage-adjusted amount
     * @param amount Original amount
     * @param slippageTolerance Slippage tolerance in basis points
     * @return adjustedAmount Amount adjusted for slippage
     */
    function _calculateSlippageAmount(
        uint256 amount,
        uint256 slippageTolerance
    ) internal pure returns (uint256 adjustedAmount) {
        uint256 slippageAmount = (amount * slippageTolerance) / 10000;
        adjustedAmount = amount - slippageAmount;
    }

    /**
     * @notice Execute DCA trade (placeholder)
     * @param intent The DCA intent
     * @param amount Amount to trade
     * @param price Current price
     */
    function _executeDCATrade(
        AdvancedIntent storage intent,
        uint256 amount,
        int256 price
    ) internal {
        // In production, this would integrate with DEX aggregators
        // For now, we simulate the trade and cross-chain send
        _simulateCrossChainSend(Intent({
            id: intent.id,
            owner: intent.user,
            intentType: IntentType.SEND_IF_PRICE_ABOVE,
            triggerPrice: price,
            amount: amount,
            tokenAddress: intent.tokenAddress,
            destinationChainSelector: intent.destinationChainSelector,
            destinationReceiver: intent.destinationReceiver,
            status: IntentStatus.EXECUTED,
            createdAt: intent.lastExecution,
            lastChecked: block.timestamp
        }));
    }

    /**
     * @notice Execute range trade (placeholder)
     * @param intent The range intent
     * @param amount Amount to trade
     * @param isBuy Whether this is a buy or sell
     */
    function _executeRangeTrade(
        AdvancedIntent storage intent,
        uint256 amount,
        bool isBuy
    ) internal {
        // In production, this would execute the actual trade
        // For now, we simulate the trade
        isBuy; // silence warning
        
        _simulateCrossChainSend(Intent({
            id: intent.id,
            owner: intent.user,
            intentType: IntentType.SEND_IF_PRICE_ABOVE,
            triggerPrice: getCurrentPrice(),
            amount: amount,
            tokenAddress: intent.tokenAddress,
            destinationChainSelector: intent.destinationChainSelector,
            destinationReceiver: intent.destinationReceiver,
            status: IntentStatus.EXECUTED,
            createdAt: intent.lastExecution,
            lastChecked: block.timestamp
        }));
    }

    /**
     * @notice Add support for a yield protocol
     * @param protocol Address of the yield protocol
     * @param supported Whether the protocol is supported
     */
    function setSupportedYieldProtocol(address protocol, bool supported) external onlyOwner {
        supportedYieldProtocols[protocol] = supported;
    }

    /**
     * @notice Get user's advanced intents
     * @param user User address
     * @return intentIds Array of intent IDs
     */
    function getUserAdvancedIntents(address user) external view returns (uint256[] memory) {
        return userAdvancedIntents[user];
    }

    /**
     * @notice Get advanced intent details
     * @param intentId Intent ID
     * @return intent The advanced intent details
     */
    function getAdvancedIntentDetails(uint256 intentId) 
        external 
        view 
        returns (AdvancedIntent memory) 
    {
        return advancedIntents[intentId];
    }

    /**
     * @notice Cancel an advanced intent
     * @param intentId Intent ID to cancel
     */
    function cancelAdvancedIntent(uint256 intentId) external validAdvancedIntent(intentId) {
        AdvancedIntent storage intent = advancedIntents[intentId];
        require(intent.user == msg.sender, "Not intent owner");

        intent.isActive = false;

        // Refund any remaining tokens
        if (intent.advancedType == AdvancedIntentType.DCA_BUY) {
            DCAParams memory params = abi.decode(intent.extraData, (DCAParams));
            uint256 remainingExecutions = intent.maxExecutions - intent.executionCount;
            uint256 refundAmount = params.investmentAmount * remainingExecutions;
            
            if (refundAmount > 0) {
                IERC20(params.targetToken).transfer(msg.sender, refundAmount);
            }
        }

        emit IntentCancelled(intentId);
    }

    /**
     * @notice Emergency pause for advanced intents
     */
    function pauseAdvancedIntents() external onlyOwner {
        // Implementation for emergency pause
        // This would disable all advanced intent executions
    }
}
