// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {IntentFi} from "../src/IntentFi.sol";

/**
 * @title IntentFiUsageExample
 * @notice Example contract showing how to interact with IntentFi
 * @dev This demonstrates integration patterns for your React Native app
 */
contract IntentFiUsageExample {
    IntentFi public immutable intentFi;
    
    // Events that your React Native app can listen to
    event UserIntentCreated(address indexed user, uint256 indexed intentId, string description);
    event AIRecommendationAccepted(address indexed user, uint256 indexed intentId, string aiReason);
    
    constructor(address payable _intentFiAddress) {
        intentFi = IntentFi(_intentFiAddress);
    }

    /**
     * @notice Create a simple price-based intent with user-friendly parameters
     * @param triggerPriceUSD Price in USD (with 2 decimals, e.g., 350000 = $3500.00)
     * @param amountUSDC Amount in USDC (with 6 decimals)
     * @param isAbove True if trigger when price is above, false if below
     * @param destinationChain Target chain selector
     * @param receiver Receiver address
     * @param description Human-readable description
     */
    function createSimpleIntent(
        uint256 triggerPriceUSD,
        uint256 amountUSDC,
        bool isAbove,
        uint64 destinationChain,
        address receiver,
        address usdcToken,
        string calldata description
    ) external returns (uint256 intentId) {
        // Convert price from 2 decimals to 8 decimals for Chainlink price feed
        int256 triggerPrice = int256(triggerPriceUSD * 1e6);
        
        // Determine intent type
        IntentFi.IntentType intentType = isAbove ? 
            IntentFi.IntentType.SEND_IF_PRICE_ABOVE : 
            IntentFi.IntentType.SEND_IF_PRICE_BELOW;
        
        // Create the intent
        intentId = intentFi.createIntent(
            intentType,
            triggerPrice,
            amountUSDC,
            usdcToken,
            destinationChain,
            receiver
        );
        
        emit UserIntentCreated(msg.sender, intentId, description);
    }

    /**
     * @notice Create an intent based on AI recommendation
     * @param recommendation The AI recommendation data
     * @param aiReason The AI's reasoning for this recommendation
     */
    function createAIRecommendedIntent(
        AIRecommendation calldata recommendation,
        string calldata aiReason
    ) external returns (uint256 intentId) {
        intentId = intentFi.createIntent(
            recommendation.intentType,
            recommendation.triggerPrice,
            recommendation.amount,
            recommendation.tokenAddress,
            recommendation.destinationChain,
            recommendation.receiver
        );
        
        emit AIRecommendationAccepted(msg.sender, intentId, aiReason);
    }

    /**
     * @notice Struct for AI recommendations from your ASI agent
     */
    struct AIRecommendation {
        IntentFi.IntentType intentType;
        int256 triggerPrice;
        uint256 amount;
        address tokenAddress;
        uint64 destinationChain;
        address receiver;
        uint256 confidence; // 0-100, AI confidence level
        string marketReason; // AI's market analysis
    }

    /**
     * @notice Get user's active intents with details
     * @param user User address
     * @return intents Array of intent details
     */
    function getUserIntentsWithDetails(address user) external view returns (IntentFi.Intent[] memory intents) {
        uint256[] memory intentIds = intentFi.getUserIntents(user);
        intents = new IntentFi.Intent[](intentIds.length);
        
        for (uint256 i = 0; i < intentIds.length; i++) {
            intents[i] = intentFi.getIntentDetails(intentIds[i]);
        }
    }

    /**
     * @notice Check if user's intents are ready for execution
     * @param user User address
     * @return readyIntents Array of intent IDs ready for execution
     */
    function getUserReadyIntents(address user) external view returns (uint256[] memory readyIntents) {
        uint256[] memory intentIds = intentFi.getUserIntents(user);
        uint256[] memory tempReady = new uint256[](intentIds.length);
        uint256 count = 0;
        
        int256 currentPrice = intentFi.getCurrentPrice();
        
        for (uint256 i = 0; i < intentIds.length; i++) {
            IntentFi.Intent memory intent = intentFi.getIntentDetails(intentIds[i]);
            
            if (intent.status == IntentFi.IntentStatus.ACTIVE) {
                bool shouldExecute = false;
                
                if (intent.intentType == IntentFi.IntentType.SEND_IF_PRICE_ABOVE) {
                    shouldExecute = currentPrice >= intent.triggerPrice;
                } else if (intent.intentType == IntentFi.IntentType.SEND_IF_PRICE_BELOW) {
                    shouldExecute = currentPrice <= intent.triggerPrice;
                }
                
                if (shouldExecute) {
                    tempReady[count] = intentIds[i];
                    count++;
                }
            }
        }
        
        // Resize array
        readyIntents = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            readyIntents[i] = tempReady[i];
        }
    }

    /**
     * @notice Get market summary for the React Native app
     * @return marketData Current market information
     */
    function getMarketSummary() external view returns (MarketData memory marketData) {
        int256 currentPrice = intentFi.getCurrentPrice();
        uint256[] memory activeIntents = intentFi.getActiveIntents();
        
        marketData = MarketData({
            currentETHPriceUSD: uint256(currentPrice),
            totalActiveIntents: activeIntents.length,
            lastUpdated: block.timestamp
        });
    }

    struct MarketData {
        uint256 currentETHPriceUSD;
        uint256 totalActiveIntents;
        uint256 lastUpdated;
    }

    /**
     * @notice Helper function to estimate intent execution
     * @param triggerPrice The trigger price
     * @param isAbove Whether trigger is above current price
     * @return likelihood Estimated likelihood of execution (0-100)
     * @return timeEstimate Estimated time to execution in seconds
     */
    function estimateIntentExecution(
        int256 triggerPrice,
        bool isAbove
    ) external view returns (uint256 likelihood, uint256 timeEstimate) {
        int256 currentPrice = intentFi.getCurrentPrice();
        
        if (isAbove) {
            if (currentPrice >= triggerPrice) {
                return (100, 0); // Already ready
            } else {
                uint256 percentageAway = uint256((triggerPrice - currentPrice) * 100 / currentPrice);
                likelihood = percentageAway > 50 ? 10 : 90 - (percentageAway * 2);
                timeEstimate = percentageAway * 3600; // Rough estimate
            }
        } else {
            if (currentPrice <= triggerPrice) {
                return (100, 0); // Already ready
            } else {
                uint256 percentageAway = uint256((currentPrice - triggerPrice) * 100 / currentPrice);
                likelihood = percentageAway > 50 ? 10 : 90 - (percentageAway * 2);
                timeEstimate = percentageAway * 3600; // Rough estimate
            }
        }
    }
}
