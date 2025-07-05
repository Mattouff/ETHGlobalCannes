// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Test, console2} from "forge-std/Test.sol";
import {IntentFiAdvanced} from "../src/IntentFiAdvanced.sol";
import {IntentFiGovernance} from "../src/IntentFiGovernance.sol";
import {MockV3Aggregator} from "./mocks/MockV3Aggregator.sol";
import {MockERC20} from "./mocks/MockERC20.sol";

/**
 * @title IntentFiAdvancedTest
 * @notice Comprehensive tests for advanced IntentFi features
 */
contract IntentFiAdvancedTest is Test {
    IntentFiAdvanced public intentFiAdvanced;
    IntentFiGovernance public governance;
    MockV3Aggregator public priceFeed;
    MockERC20 public usdc;
    MockERC20 public governanceToken;
    MockERC20 public linkToken;
    
    address public constant CCIP_ROUTER = address(0x1234);
    address public user1 = makeAddr("user1");
    address public user2 = makeAddr("user2");
    address public user3 = makeAddr("user3");
    address public owner = makeAddr("owner");
    
    uint256 public constant INITIAL_PRICE = 3500e8; // $3500
    uint256 public constant INITIAL_BALANCE = 1000e6; // 1000 USDC
    uint256 public constant INITIAL_GOV_TOKENS = 1000000e18; // 1M governance tokens

    event AdvancedIntentCreated(
        uint256 indexed id,
        address indexed user,
        IntentFiAdvanced.AdvancedIntentType advancedType,
        uint256 amount
    );

    event DCAExecuted(
        uint256 indexed intentId,
        uint256 executionNumber,
        uint256 amount,
        int256 price
    );

    function setUp() public {
        // Deploy mock contracts
        priceFeed = new MockV3Aggregator(8, int256(INITIAL_PRICE));
        usdc = new MockERC20("USDC", "USDC", 6);
        linkToken = new MockERC20("LINK", "LINK", 18);
        governanceToken = new MockERC20("IntentFi Token", "IFI", 18);
        
        // Deploy main contracts
        vm.startPrank(owner);
        intentFiAdvanced = new IntentFiAdvanced(
            address(priceFeed),
            CCIP_ROUTER,
            address(linkToken)
        );
        
        address[] memory emergencyMultisig = new address[](3);
        emergencyMultisig[0] = owner;
        emergencyMultisig[1] = user1;
        emergencyMultisig[2] = user2;
        
        governance = new IntentFiGovernance(
            address(governanceToken),
            owner,
            emergencyMultisig
        );
        vm.stopPrank();
        
        // Setup token balances
        usdc.mint(user1, INITIAL_BALANCE);
        usdc.mint(user2, INITIAL_BALANCE);
        usdc.mint(user3, INITIAL_BALANCE);
        
        governanceToken.mint(user1, INITIAL_GOV_TOKENS);
        governanceToken.mint(user2, INITIAL_GOV_TOKENS);
        governanceToken.mint(user3, 50000e18); // User3 has less voting power (below threshold)
        
        linkToken.mint(address(intentFiAdvanced), 100e18); // Fund contract with LINK
        
        // Configure contracts
        vm.startPrank(owner);
        intentFiAdvanced.setSupportedToken(address(usdc), true);
        intentFiAdvanced.allowlistDestinationChain(10344971235874465080, true); // Base Sepolia
        vm.stopPrank();
    }

    // =========================
    // DCA Tests
    // =========================

    function test_CreateDCAIntent() public {
        IntentFiAdvanced.DCAParams memory params = IntentFiAdvanced.DCAParams({
            investmentAmount: 20e6,
            intervalSeconds: 3600,
            totalPeriods: 10,
            targetToken: address(usdc),
            slippageTolerance: 200
        });
        
        vm.startPrank(user1);
        usdc.approve(address(intentFiAdvanced), 200e6);
        
        vm.expectEmit(true, true, false, true);
        emit AdvancedIntentCreated(1, user1, IntentFiAdvanced.AdvancedIntentType.DCA_BUY, 200e6);
        
        uint256 intentId = intentFiAdvanced.createDCAIntent(
            params,
            10344971235874465080,
            user1
        );
        vm.stopPrank();
        
        assertEq(intentId, 1);
        
        IntentFiAdvanced.AdvancedIntent memory intent = intentFiAdvanced.getAdvancedIntentDetails(intentId);
        assertEq(intent.user, user1);
        assertEq(uint8(intent.advancedType), uint8(IntentFiAdvanced.AdvancedIntentType.DCA_BUY));
        assertEq(intent.amount, 200e6);
        assertEq(intent.frequency, 3600);
        assertEq(intent.maxExecutions, 10);
        assertTrue(intent.isActive);
    }

    function test_RevertIf_DCAInvalidParams() public {
        IntentFiAdvanced.DCAParams memory params = IntentFiAdvanced.DCAParams({
            investmentAmount: 0, // Invalid: zero amount
            intervalSeconds: 3600,
            totalPeriods: 10,
            targetToken: address(usdc),
            slippageTolerance: 200
        });
        
        vm.startPrank(user1);
        usdc.approve(address(intentFiAdvanced), 200e6);
        
        vm.expectRevert("Investment amount must be > 0");
        intentFiAdvanced.createDCAIntent(params, 10344971235874465080, user1);
        vm.stopPrank();
    }

    function test_ExecuteDCAIntent() public {
        // Create DCA intent
        IntentFiAdvanced.DCAParams memory params = IntentFiAdvanced.DCAParams({
            investmentAmount: 20e6,
            intervalSeconds: 3600,
            totalPeriods: 10,
            targetToken: address(usdc),
            slippageTolerance: 200
        });
        
        vm.startPrank(user1);
        usdc.approve(address(intentFiAdvanced), 200e6);
        uint256 intentId = intentFiAdvanced.createDCAIntent(params, 10344971235874465080, user1);
        vm.stopPrank();
        
        // Fast forward time
        vm.warp(block.timestamp + 3601);
        
        // Execute DCA
        vm.expectEmit(true, false, false, false);
        emit DCAExecuted(intentId, 1, 0, int256(INITIAL_PRICE)); // Amount will be adjusted for slippage
        
        intentFiAdvanced.executeDCAIntent(intentId);
        
        IntentFiAdvanced.AdvancedIntent memory intent = intentFiAdvanced.getAdvancedIntentDetails(intentId);
        assertEq(intent.executionCount, 1);
        assertEq(intent.lastExecution, block.timestamp);
    }

    function test_RevertIf_DCAExecuteTooEarly() public {
        // Create DCA intent
        IntentFiAdvanced.DCAParams memory params = IntentFiAdvanced.DCAParams({
            investmentAmount: 20e6,
            intervalSeconds: 3600,
            totalPeriods: 10,
            targetToken: address(usdc),
            slippageTolerance: 200
        });
        
        vm.startPrank(user1);
        usdc.approve(address(intentFiAdvanced), 200e6);
        uint256 intentId = intentFiAdvanced.createDCAIntent(params, 10344971235874465080, user1);
        vm.stopPrank();
        
        // Try to execute immediately (should fail)
        vm.expectRevert("Too early for next execution");
        intentFiAdvanced.executeDCAIntent(intentId);
    }

    // =========================
    // Range Trading Tests
    // =========================

    function test_CreateRangeIntent() public {
        IntentFiAdvanced.RangeParams memory params = IntentFiAdvanced.RangeParams({
            buyPrice: 3000e8,  // $3000
            sellPrice: 4000e8, // $4000
            tradeAmount: 50e6,
            maxTrades: 5
        });
        
        vm.startPrank(user2);
        usdc.approve(address(intentFiAdvanced), 250e6);
        
        uint256 intentId = intentFiAdvanced.createRangeIntent(
            params,
            10344971235874465080,
            user2
        );
        vm.stopPrank();
        
        IntentFiAdvanced.AdvancedIntent memory intent = intentFiAdvanced.getAdvancedIntentDetails(intentId);
        assertEq(intent.user, user2);
        assertEq(uint8(intent.advancedType), uint8(IntentFiAdvanced.AdvancedIntentType.RANGE_TRADING));
        assertEq(intent.lowerBound, 3000e8);
        assertEq(intent.upperBound, 4000e8);
        assertEq(intent.maxExecutions, 5);
    }

    function test_ExecuteRangeIntent_Buy() public {
        // Create range intent
        IntentFiAdvanced.RangeParams memory params = IntentFiAdvanced.RangeParams({
            buyPrice: 3600e8,  // Above current price to trigger buy
            sellPrice: 4000e8,
            tradeAmount: 50e6,
            maxTrades: 5
        });
        
        vm.startPrank(user2);
        usdc.approve(address(intentFiAdvanced), 250e6);
        uint256 intentId = intentFiAdvanced.createRangeIntent(params, 10344971235874465080, user2);
        vm.stopPrank();
        
        // Set price to trigger buy condition
        priceFeed.updateAnswer(3500e8); // Below buy price, should trigger buy
        
        intentFiAdvanced.executeRangeIntent(intentId);
        
        IntentFiAdvanced.AdvancedIntent memory intent = intentFiAdvanced.getAdvancedIntentDetails(intentId);
        assertEq(intent.executionCount, 1);
    }

    function test_RevertIf_RangeIntentInvalidPrice() public {
        // Price not in execution range (between buy and sell prices)
        IntentFiAdvanced.RangeParams memory params = IntentFiAdvanced.RangeParams({
            buyPrice: 3400e8,  // Below current price (3500)
            sellPrice: 3600e8, // Above current price (3500)
            tradeAmount: 50e6,
            maxTrades: 5
        });
        
        vm.startPrank(user2);
        usdc.approve(address(intentFiAdvanced), 250e6);
        uint256 intentId = intentFiAdvanced.createRangeIntent(params, 10344971235874465080, user2);
        vm.stopPrank();
        
        vm.expectRevert("Price not in execution range");
        intentFiAdvanced.executeRangeIntent(intentId);
    }

    // =========================
    // Yield Farming Tests
    // =========================

    function test_CreateYieldIntent() public {
        address mockYieldProtocol = makeAddr("yieldProtocol");
        
        // Add supported yield protocol
        vm.prank(owner);
        intentFiAdvanced.setSupportedYieldProtocol(mockYieldProtocol, true);
        
        IntentFiAdvanced.YieldParams memory params = IntentFiAdvanced.YieldParams({
            yieldProtocol: mockYieldProtocol,
            minYield: 500, // 5%
            stakingAmount: 100e6,
            compoundFrequency: 86400 // Daily
        });
        
        vm.startPrank(user3);
        uint256 intentId = intentFiAdvanced.createYieldIntent(
            params,
            10344971235874465080,
            user3
        );
        vm.stopPrank();
        
        IntentFiAdvanced.AdvancedIntent memory intent = intentFiAdvanced.getAdvancedIntentDetails(intentId);
        assertEq(intent.user, user3);
        assertEq(uint8(intent.advancedType), uint8(IntentFiAdvanced.AdvancedIntentType.YIELD_FARMING));
        assertEq(intent.amount, 100e6);
    }

    function test_RevertIf_UnsupportedYieldProtocol() public {
        address unsupportedProtocol = makeAddr("unsupportedProtocol");
        
        IntentFiAdvanced.YieldParams memory params = IntentFiAdvanced.YieldParams({
            yieldProtocol: unsupportedProtocol,
            minYield: 500,
            stakingAmount: 100e6,
            compoundFrequency: 86400
        });
        
        vm.startPrank(user3);
        vm.expectRevert("Unsupported yield protocol");
        intentFiAdvanced.createYieldIntent(params, 10344971235874465080, user3);
        vm.stopPrank();
    }

    // =========================
    // Cancel Advanced Intent Tests
    // =========================

    function test_CancelAdvancedIntent() public {
        // Create DCA intent
        IntentFiAdvanced.DCAParams memory params = IntentFiAdvanced.DCAParams({
            investmentAmount: 20e6,
            intervalSeconds: 3600,
            totalPeriods: 10,
            targetToken: address(usdc),
            slippageTolerance: 200
        });
        
        vm.startPrank(user1);
        usdc.approve(address(intentFiAdvanced), 200e6);
        uint256 intentId = intentFiAdvanced.createDCAIntent(params, 10344971235874465080, user1);
        
        uint256 balanceBefore = usdc.balanceOf(user1);
        
        // Cancel intent
        intentFiAdvanced.cancelAdvancedIntent(intentId);
        vm.stopPrank();
        
        // Check intent is deactivated
        IntentFiAdvanced.AdvancedIntent memory intent = intentFiAdvanced.getAdvancedIntentDetails(intentId);
        assertFalse(intent.isActive);
        
        // Check refund
        uint256 balanceAfter = usdc.balanceOf(user1);
        assertEq(balanceAfter, balanceBefore + 200e6); // Full refund since no executions
    }

    function test_RevertIf_CancelNotOwner() public {
        // Create intent as user1
        IntentFiAdvanced.DCAParams memory params = IntentFiAdvanced.DCAParams({
            investmentAmount: 20e6,
            intervalSeconds: 3600,
            totalPeriods: 10,
            targetToken: address(usdc),
            slippageTolerance: 200
        });
        
        vm.startPrank(user1);
        usdc.approve(address(intentFiAdvanced), 200e6);
        uint256 intentId = intentFiAdvanced.createDCAIntent(params, 10344971235874465080, user1);
        vm.stopPrank();
        
        // Try to cancel as user2
        vm.prank(user2);
        vm.expectRevert("Not intent owner");
        intentFiAdvanced.cancelAdvancedIntent(intentId);
    }

    // =========================
    // Governance Tests
    // =========================

    function test_CreateGovernanceProposal() public {
        vm.startPrank(user1);
        uint256 proposalId = governance.propose(
            "Test Proposal",
            "A test proposal for the governance system",
            address(intentFiAdvanced),
            0,
            abi.encodeWithSignature("updateProtocolFee(uint256)", 50)
        );
        vm.stopPrank();
        
        assertEq(proposalId, 1);
        
        (
            address proposer,
            string memory title,
            string memory description,
            uint256 startTime,
            uint256 endTime,
            uint256 forVotes,
            uint256 againstVotes,
            uint256 abstainVotes,
            bool executed,
            bool cancelled
        ) = governance.getProposalDetails(proposalId);
        
        assertEq(proposer, user1);
        assertEq(title, "Test Proposal");
        assertEq(description, "A test proposal for the governance system");
        assertGt(startTime, block.timestamp);
        assertGt(endTime, startTime);
    }

    function test_RevertIf_InsufficientVotingPower() public {
        // User3 has less governance tokens, should fail threshold
        vm.startPrank(user3);
        vm.expectRevert("Insufficient voting power");
        governance.propose(
            "Test Proposal",
            "A test proposal",
            address(intentFiAdvanced),
            0,
            ""
        );
        vm.stopPrank();
    }

    function test_VoteOnProposal() public {
        // Create proposal
        vm.startPrank(user1);
        uint256 proposalId = governance.propose(
            "Test Proposal",
            "A test proposal",
            address(intentFiAdvanced),
            0,
            ""
        );
        vm.stopPrank();
        
        // Fast forward to voting period
        vm.warp(block.timestamp + 1 days + 1);
        
        // Cast votes
        vm.prank(user1);
        governance.castVote(proposalId, true, false); // Vote yes
        
        vm.prank(user2);
        governance.castVote(proposalId, false, false); // Vote no
        
        // Check vote counts
        (,,,,, uint256 forVotes, uint256 againstVotes, uint256 abstainVotes,,) = 
            governance.getProposalDetails(proposalId);
        
        assertEq(forVotes, INITIAL_GOV_TOKENS);
        assertEq(againstVotes, INITIAL_GOV_TOKENS);
        assertEq(abstainVotes, 0);
    }

    function test_RevertIf_VoteAlreadyCast() public {
        // Create proposal
        vm.startPrank(user1);
        uint256 proposalId = governance.propose(
            "Test Proposal",
            "A test proposal",
            address(intentFiAdvanced),
            0,
            ""
        );
        vm.stopPrank();
        
        // Fast forward to voting period
        vm.warp(block.timestamp + 1 days + 1);
        
        // Cast vote
        vm.prank(user1);
        governance.castVote(proposalId, true, false);
        
        // Try to vote again
        vm.prank(user1);
        vm.expectRevert("Already voted");
        governance.castVote(proposalId, false, false);
    }

    function test_EmergencyPause() public {
        vm.prank(owner);
        governance.emergencyPause();
        
        (,,,,, bool paused) = governance.protocolParams();
        assertTrue(paused);
    }

    function test_RevertIf_EmergencyPauseNotAuthorized() public {
        vm.prank(user3); // Not in emergency multisig
        vm.expectRevert("Not emergency multisig");
        governance.emergencyPause();
    }

    // =========================
    // Utility Functions
    // =========================

    function test_GetUserAdvancedIntents() public {
        // Create multiple intents for user1
        IntentFiAdvanced.DCAParams memory dcaParams = IntentFiAdvanced.DCAParams({
            investmentAmount: 20e6,
            intervalSeconds: 3600,
            totalPeriods: 10,
            targetToken: address(usdc),
            slippageTolerance: 200
        });
        
        IntentFiAdvanced.RangeParams memory rangeParams = IntentFiAdvanced.RangeParams({
            buyPrice: 3000e8,
            sellPrice: 4000e8,
            tradeAmount: 50e6,
            maxTrades: 5
        });
        
        vm.startPrank(user1);
        usdc.approve(address(intentFiAdvanced), 450e6);
        
        uint256 dcaId = intentFiAdvanced.createDCAIntent(dcaParams, 10344971235874465080, user1);
        uint256 rangeId = intentFiAdvanced.createRangeIntent(rangeParams, 10344971235874465080, user1);
        vm.stopPrank();
        
        uint256[] memory userIntents = intentFiAdvanced.getUserAdvancedIntents(user1);
        assertEq(userIntents.length, 2);
        assertEq(userIntents[0], dcaId);
        assertEq(userIntents[1], rangeId);
    }

    function test_CalculateSlippageAmount() public {
        // This would test the internal _calculateSlippageAmount function
        // Since it's internal, we'll test it through DCA execution
        
        IntentFiAdvanced.DCAParams memory params = IntentFiAdvanced.DCAParams({
            investmentAmount: 100e6, // 100 USDC
            intervalSeconds: 3600,
            totalPeriods: 1,
            targetToken: address(usdc),
            slippageTolerance: 500 // 5% slippage
        });
        
        vm.startPrank(user1);
        usdc.approve(address(intentFiAdvanced), 100e6);
        uint256 intentId = intentFiAdvanced.createDCAIntent(params, 10344971235874465080, user1);
        vm.stopPrank();
        
        vm.warp(block.timestamp + 3601);
        
        // The execution should apply 5% slippage, so 95 USDC effective trade
        intentFiAdvanced.executeDCAIntent(intentId);
        
        // Verify execution happened (specific amounts would depend on implementation)
        IntentFiAdvanced.AdvancedIntent memory intent = intentFiAdvanced.getAdvancedIntentDetails(intentId);
        assertEq(intent.executionCount, 1);
    }
}
