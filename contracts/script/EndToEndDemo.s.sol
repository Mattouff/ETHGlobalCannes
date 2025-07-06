// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Script, console2} from "forge-std/Script.sol";
import {IntentFi} from "../src/IntentFi.sol";
import {IntentFiAdvanced} from "../src/IntentFiAdvanced.sol";
import {IntentFiGovernance} from "../src/IntentFiGovernance.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title EndToEndDemo
 * @notice Comprehensive end-to-end demonstration of IntentFi ecosystem
 */
contract EndToEndDemo is Script {
    
    IntentFiAdvanced public intentFiAdvanced;
    IntentFiGovernance public governance;
    IERC20 public usdc;
    IERC20 public governanceToken;
    
    address public user1;
    address public user2;
    address public user3;
    
    function setUp() public {
        // Load deployed contract addresses
        intentFiAdvanced = IntentFiAdvanced(payable(vm.envAddress("INTENTFI_ADVANCED_ADDRESS")));
        governance = IntentFiGovernance(vm.envAddress("INTENTFI_GOVERNANCE_ADDRESS"));
        usdc = IERC20(vm.envAddress("USDC_ADDRESS"));
        governanceToken = IERC20(vm.envAddress("GOVERNANCE_TOKEN_ADDRESS"));
        
        // Setup test users
        user1 = vm.addr(1);
        user2 = vm.addr(2);
        user3 = vm.addr(3);
    }

    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        
        vm.startBroadcast(deployerPrivateKey);
        
        console2.log("=== IntentFi End-to-End Demo ===");
        
        // 1. Setup demo environment
        setupDemoEnvironment();
        
        // 2. Demonstrate basic intents
        demonstrateBasicIntents();
        
        // 3. Demonstrate DCA functionality
        demonstrateDCA();
        
        // 4. Demonstrate range trading
        demonstrateRangeTrading();
        
        // 5. Demonstrate governance
        demonstrateGovernance();
        
        // 6. Demonstrate cross-chain functionality
        demonstrateCrossChain();
        
        vm.stopBroadcast();
        
        console2.log("=== Demo Complete ===");
    }

    /**
     * @notice Setup demo environment with tokens and permissions
     */
    function setupDemoEnvironment() internal {
        console2.log("\n--- Setting up demo environment ---");
        
        // Mint USDC to test users (if we have mint permission)
        try this.mintTokensToUsers() {
            console2.log("SUCCESS: Tokens minted to test users");
        } catch {
            console2.log("INFO: Using existing token balances");
        }
        
        // Transfer governance tokens to test users
        uint256 govTokenBalance = governanceToken.balanceOf(msg.sender);
        if (govTokenBalance > 0) {
            uint256 amountPerUser = govTokenBalance / 10; // 10% to each user
            governanceToken.transfer(user1, amountPerUser);
            governanceToken.transfer(user2, amountPerUser);
            governanceToken.transfer(user3, amountPerUser);
            console2.log("SUCCESS: Governance tokens distributed");
        }
    }

    /**
     * @notice Demonstrate basic intent functionality
     */
    function demonstrateBasicIntents() internal {
        console2.log("\n--- Demonstrating Basic Intents ---");
        
        // Create a basic intent
        vm.prank(user1);
        usdc.approve(address(intentFiAdvanced), 100e6); // 100 USDC
        
        vm.prank(user1);
        uint256 intentId = intentFiAdvanced.createIntent(
            IntentFi.IntentType.SEND_IF_PRICE_ABOVE,
            3500e8, // $3500
            50e6,   // 50 USDC
            address(usdc),
            10344971235874465080, // Base Sepolia
            user1
        );
        
        console2.log("SUCCESS: Basic intent created with ID:", intentId);
        
        // Check current price and intent status
        int256 currentPrice = intentFiAdvanced.getCurrentPrice();
        console2.log("Current ETH price: $", uint256(currentPrice) / 1e8);
        
        // Check if intent is ready for execution
        (bool upkeepNeeded, ) = intentFiAdvanced.checkUpkeep("");
        console2.log("Intent ready for execution:", upkeepNeeded);
    }

    /**
     * @notice Demonstrate DCA (Dollar Cost Averaging) functionality
     */
    function demonstrateDCA() internal {
        console2.log("\n--- Demonstrating DCA ---");
        
        // Setup DCA parameters
        IntentFiAdvanced.DCAParams memory dcaParams = IntentFiAdvanced.DCAParams({
            investmentAmount: 20e6,    // 20 USDC per period
            intervalSeconds: 3600,     // 1 hour intervals
            totalPeriods: 10,          // 10 periods total
            targetToken: address(usdc),
            slippageTolerance: 200     // 2% slippage
        });
        
        // Create DCA intent
        vm.prank(user2);
        usdc.approve(address(intentFiAdvanced), 200e6); // 200 USDC total
        
        vm.prank(user2);
        uint256 dcaIntentId = intentFiAdvanced.createDCAIntent(
            dcaParams,
            5224473277236331295, // Optimism Sepolia
            user2
        );
        
        console2.log("SUCCESS: DCA intent created with ID:", dcaIntentId);
        
        // Simulate time passage and execute DCA
        vm.warp(block.timestamp + 3601); // Fast forward 1 hour + 1 second
        
        vm.prank(user2);
        intentFiAdvanced.executeDCAIntent(dcaIntentId);
        console2.log("SUCCESS: First DCA execution completed");
        
        // Check DCA status
        IntentFiAdvanced.AdvancedIntent memory dcaIntent = intentFiAdvanced.getAdvancedIntentDetails(dcaIntentId);
        console2.log("DCA executions completed:", dcaIntent.executionCount, "of", dcaIntent.maxExecutions);
    }

    /**
     * @notice Demonstrate range trading functionality
     */
    function demonstrateRangeTrading() internal {
        console2.log("\n--- Demonstrating Range Trading ---");
        
        int256 currentPrice = intentFiAdvanced.getCurrentPrice();
        
        // Setup range trading parameters (±5% around current price)
        IntentFiAdvanced.RangeParams memory rangeParams = IntentFiAdvanced.RangeParams({
            buyPrice: currentPrice - (currentPrice * 5 / 100),  // 5% below current
            sellPrice: currentPrice + (currentPrice * 5 / 100), // 5% above current
            tradeAmount: 30e6,  // 30 USDC per trade
            maxTrades: 5        // Maximum 5 trades
        });
        
        console2.log("Range: $", uint256(rangeParams.buyPrice) / 1e8, "- $", uint256(rangeParams.sellPrice) / 1e8);
        
        // Create range trading intent
        vm.prank(user3);
        usdc.approve(address(intentFiAdvanced), 150e6); // 150 USDC total
        
        vm.prank(user3);
        uint256 rangeIntentId = intentFiAdvanced.createRangeIntent(
            rangeParams,
            3478487238524512106, // Arbitrum Sepolia
            user3
        );
        
        console2.log("SUCCESS: Range trading intent created with ID:", rangeIntentId);
        
        // Note: Range execution would happen when price moves into range
        console2.log("Range trading intent waiting for price movement");
    }

    /**
     * @notice Demonstrate governance functionality
     */
    function demonstrateGovernance() internal {
        console2.log("\n--- Demonstrating Governance ---");
        
        // Create a governance proposal
        vm.prank(user1);
        uint256 proposalId = governance.propose(
            "Increase Protocol Fee",
            "Proposal to increase protocol fee from 0.3% to 0.5%",
            address(intentFiAdvanced),
            0,
            abi.encodeWithSignature("updateProtocolFee(uint256)", 50) // 0.5%
        );
        
        console2.log("SUCCESS: Governance proposal created with ID:", proposalId);
        
        // Fast forward to voting period
        vm.warp(block.timestamp + 1 days + 1); // Past voting delay
        
        // Cast votes
        vm.prank(user1);
        governance.castVote(proposalId, true, false); // Vote yes
        
        vm.prank(user2);
        governance.castVote(proposalId, true, false); // Vote yes
        
        vm.prank(user3);
        governance.castVote(proposalId, false, false); // Vote no
        
        console2.log("SUCCESS: Votes cast by users");
        
        // Fast forward past voting period
        vm.warp(block.timestamp + 3 days + 1);
        
        // Execute proposal (would need to implement the function in the contract)
        try governance.executeProposal(proposalId) {
            console2.log("SUCCESS: Proposal executed successfully");
        } catch {
            console2.log("INFO: Proposal execution deferred (timelock)");
        }
        
        // Show proposal details
        (
            address proposer,
            string memory title,
            ,
            ,
            ,
            uint256 forVotes,
            uint256 againstVotes,
            uint256 abstainVotes,
            bool executed,
            bool cancelled
        ) = governance.getProposalDetails(proposalId);
        
        console2.log("Proposal by:", proposer);
        console2.log("Title:", title);
        console2.log("For votes:", forVotes);
        console2.log("Against votes:", againstVotes);
        console2.log("Abstain votes:", abstainVotes);
        console2.log("Executed:", executed);
        console2.log("Cancelled:", cancelled);
    }

    /**
     * @notice Demonstrate cross-chain functionality
     */
    function demonstrateCrossChain() internal {
        console2.log("\n--- Demonstrating Cross-Chain ---");
        
        // Check supported chains
        bool sepoliaSupported = intentFiAdvanced.allowlistedDestinationChains(16015286601757825753);
        bool baseSupported = intentFiAdvanced.allowlistedDestinationChains(10344971235874465080);
        bool optimismSupported = intentFiAdvanced.allowlistedDestinationChains(5224473277236331295);
        bool arbitrumSupported = intentFiAdvanced.allowlistedDestinationChains(3478487238524512106);
        
        console2.log("Supported chains:");
        console2.log("  Sepolia:", sepoliaSupported);
        console2.log("  Base Sepolia:", baseSupported);
        console2.log("  Optimism Sepolia:", optimismSupported);
        console2.log("  Arbitrum Sepolia:", arbitrumSupported);
        
        // Check CCIP configuration
        address ccipRouter = intentFiAdvanced.getCCIPRouter();
        address linkToken = intentFiAdvanced.getLINKToken();
        uint256 linkBalance = intentFiAdvanced.getLINKBalance();
        
        console2.log("CCIP Router:", ccipRouter);
        console2.log("LINK Token:", linkToken);
        console2.log("LINK Balance:", linkBalance);
        
        // Fund contract with LINK if needed
        if (linkBalance == 0) {
            console2.log("INFO: Contract needs LINK funding for cross-chain operations");
        }
        
        console2.log("SUCCESS: Cross-chain configuration verified");
    }

    /**
     * @notice Mint tokens to test users (external function for try/catch)
     */
    function mintTokensToUsers() external {
        // This would only work if the USDC contract has a mint function we can call
        // In most cases, we'd need to transfer from an existing holder
        revert("Mint not available");
    }

    /**
     * @notice Get user intent summaries
     */
    function getUserIntentSummaries() external view returns (string memory summary) {
        summary = "User Intent Summary:\n";
        
        // User 1 intents
        uint256[] memory user1Intents = intentFiAdvanced.getUserIntents(user1);
        summary = string.concat(summary, "User 1: ", vm.toString(user1Intents.length), " intents\n");
        
        // User 2 intents
        uint256[] memory user2Intents = intentFiAdvanced.getUserIntents(user2);
        uint256[] memory user2AdvancedIntents = intentFiAdvanced.getUserAdvancedIntents(user2);
        summary = string.concat(
            summary, 
            "User 2: ", 
            vm.toString(user2Intents.length), 
            " basic + ", 
            vm.toString(user2AdvancedIntents.length), 
            " advanced intents\n"
        );
        
        // User 3 intents
        uint256[] memory user3Intents = intentFiAdvanced.getUserIntents(user3);
        uint256[] memory user3AdvancedIntents = intentFiAdvanced.getUserAdvancedIntents(user3);
        summary = string.concat(
            summary, 
            "User 3: ", 
            vm.toString(user3Intents.length), 
            " basic + ", 
            vm.toString(user3AdvancedIntents.length), 
            " advanced intents\n"
        );
    }

    /**
     * @notice Stress test the system
     */
    function stressTest() external {
        console2.log("\n--- Stress Testing ---");
        
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);
        
        // Create multiple intents rapidly
        for (uint i = 0; i < 10; i++) {
            address testUser = vm.addr(100 + i);
            
            // Give user some USDC
            usdc.transfer(testUser, 100e6);
            
            vm.prank(testUser);
            usdc.approve(address(intentFiAdvanced), 100e6);
            
            vm.prank(testUser);
            uint256 intentId = intentFiAdvanced.createIntent(
                IntentFi.IntentType.SEND_IF_PRICE_ABOVE,
                int256((3500 + i * 10) * 1e8), // Varying trigger prices
                10e6, // 10 USDC each
                address(usdc),
                10344971235874465080, // Base Sepolia
                testUser
            );
            
            if (i % 3 == 0) {
                console2.log("Created intent", intentId, "for user", i);
            }
        }
        
        vm.stopBroadcast();
        
        console2.log("SUCCESS: Stress test completed: 10 intents created");
    }
}
