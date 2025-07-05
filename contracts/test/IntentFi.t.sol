// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Test, console2} from "forge-std/Test.sol";
import {IntentFi} from "../src/IntentFi.sol";
import {MockV3Aggregator} from "./mocks/MockV3Aggregator.sol";
import {MockERC20} from "./mocks/MockERC20.sol";

contract IntentFiTest is Test {
    IntentFi public intentFi;
    MockV3Aggregator public mockPriceFeed;
    MockERC20 public mockUSDC;
    
    address public alice = makeAddr("alice");
    address public bob = makeAddr("bob");
    address public owner = makeAddr("owner");
    address public ccipRouter = makeAddr("ccipRouter");
    
    uint64 public constant DESTINATION_CHAIN_SELECTOR = 12345;
    int256 public constant INITIAL_ETH_PRICE = 3000 * 1e8; // $3000 with 8 decimals
    uint256 public constant INTENT_AMOUNT = 50e6; // 50 USDC (6 decimals)
    
    event IntentCreated(
        uint256 indexed intentId,
        address indexed owner,
        IntentFi.IntentType intentType,
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

    function setUp() public {
        vm.startPrank(owner);
        
        // Deploy mocks
        mockPriceFeed = new MockV3Aggregator(8, INITIAL_ETH_PRICE);
        mockUSDC = new MockERC20("USD Coin", "USDC", 6);
        
        // Deploy IntentFi
        intentFi = new IntentFi(
            address(mockPriceFeed),
            ccipRouter
        );
        
        // Setup allowlisted chains
        intentFi.allowlistDestinationChain(DESTINATION_CHAIN_SELECTOR, true);
        
        vm.stopPrank();
        
        // Give Alice some tokens
        vm.startPrank(alice);
        mockUSDC.mint(alice, 1000e6); // 1000 USDC
        vm.deal(alice, 10 ether);
        vm.stopPrank();
    }

    function testCreateIntentWithUSDC() public {
        vm.startPrank(alice);
        
        // Approve USDC transfer
        mockUSDC.approve(address(intentFi), INTENT_AMOUNT);
        
        // Create intent: Send 50 USDC if ETH > $3500
        vm.expectEmit(true, true, false, true);
        emit IntentCreated(
            1,
            alice,
            IntentFi.IntentType.SEND_IF_PRICE_ABOVE,
            3500 * 1e8,
            INTENT_AMOUNT,
            DESTINATION_CHAIN_SELECTOR,
            bob
        );
        
        uint256 intentId = intentFi.createIntent(
            IntentFi.IntentType.SEND_IF_PRICE_ABOVE,
            3500 * 1e8, // $3500 trigger
            INTENT_AMOUNT,
            address(mockUSDC),
            DESTINATION_CHAIN_SELECTOR,
            bob
        );
        
        vm.stopPrank();
        
        assertEq(intentId, 1);
        assertEq(mockUSDC.balanceOf(address(intentFi)), INTENT_AMOUNT);
        
        // Check intent details
        IntentFi.Intent memory intent = intentFi.getIntentDetails(intentId);
        
        assertEq(intent.id, 1);
        assertEq(intent.owner, alice);
        assertEq(uint8(intent.intentType), uint8(IntentFi.IntentType.SEND_IF_PRICE_ABOVE));
        assertEq(intent.triggerPrice, 3500 * 1e8);
        assertEq(intent.amount, INTENT_AMOUNT);
        assertEq(intent.tokenAddress, address(mockUSDC));
        assertEq(intent.destinationChainSelector, DESTINATION_CHAIN_SELECTOR);
        assertEq(intent.destinationReceiver, bob);
        assertEq(uint8(intent.status), uint8(IntentFi.IntentStatus.ACTIVE));
    }

    function testCreateIntentWithETH() public {
        vm.startPrank(alice);
        
        uint256 ethAmount = 1 ether;
        
        // Create intent: Send 1 ETH if ETH < $2500
        uint256 intentId = intentFi.createIntent{value: ethAmount}(
            IntentFi.IntentType.SEND_IF_PRICE_BELOW,
            2500 * 1e8, // $2500 trigger
            ethAmount,
            address(0), // ETH
            DESTINATION_CHAIN_SELECTOR,
            bob
        );
        
        vm.stopPrank();
        
        assertEq(intentId, 1);
        assertEq(address(intentFi).balance, ethAmount);
    }

    function testCheckUpkeepWhenConditionNotMet() public {
        // Create intent first
        vm.startPrank(alice);
        mockUSDC.approve(address(intentFi), INTENT_AMOUNT);
        intentFi.createIntent(
            IntentFi.IntentType.SEND_IF_PRICE_ABOVE,
            3500 * 1e8, // $3500 trigger
            INTENT_AMOUNT,
            address(mockUSDC),
            DESTINATION_CHAIN_SELECTOR,
            bob
        );
        vm.stopPrank();
        
        // Current price is $3000, trigger is $3500, so should not execute
        (bool upkeepNeeded, ) = intentFi.checkUpkeep("");
        assertFalse(upkeepNeeded);
    }

    function testCheckUpkeepWhenConditionMet() public {
        // Create intent first
        vm.startPrank(alice);
        mockUSDC.approve(address(intentFi), INTENT_AMOUNT);
        intentFi.createIntent(
            IntentFi.IntentType.SEND_IF_PRICE_ABOVE,
            3500 * 1e8, // $3500 trigger
            INTENT_AMOUNT,
            address(mockUSDC),
            DESTINATION_CHAIN_SELECTOR,
            bob
        );
        vm.stopPrank();
        
        // Update price to $3600 (above trigger)
        mockPriceFeed.updateAnswer(3600 * 1e8);
        
        (bool upkeepNeeded, bytes memory performData) = intentFi.checkUpkeep("");
        assertTrue(upkeepNeeded);
        
        uint256[] memory intentIds = abi.decode(performData, (uint256[]));
        assertEq(intentIds.length, 1);
        assertEq(intentIds[0], 1);
    }

    function testPerformUpkeep() public {
        // Create intent first
        vm.startPrank(alice);
        mockUSDC.approve(address(intentFi), INTENT_AMOUNT);
        intentFi.createIntent(
            IntentFi.IntentType.SEND_IF_PRICE_ABOVE,
            3500 * 1e8,
            INTENT_AMOUNT,
            address(mockUSDC),
            DESTINATION_CHAIN_SELECTOR,
            bob
        );
        vm.stopPrank();
        
        // Update price to trigger execution
        mockPriceFeed.updateAnswer(3600 * 1e8);
        
        // Get perform data
        (, bytes memory performData) = intentFi.checkUpkeep("");
        
        // Expect IntentExecuted event
        vm.expectEmit(true, true, false, true);
        emit IntentExecuted(1, DESTINATION_CHAIN_SELECTOR, bob, INTENT_AMOUNT);
        
        // Perform upkeep
        intentFi.performUpkeep(performData);
        
        // Check intent status changed to executed
        IntentFi.Intent memory intent = intentFi.getIntentDetails(1);
        assertEq(uint8(intent.status), uint8(IntentFi.IntentStatus.EXECUTED));
    }

    function testCancelIntent() public {
        // Create intent first
        vm.startPrank(alice);
        mockUSDC.approve(address(intentFi), INTENT_AMOUNT);
        uint256 intentId = intentFi.createIntent(
            IntentFi.IntentType.SEND_IF_PRICE_ABOVE,
            3500 * 1e8,
            INTENT_AMOUNT,
            address(mockUSDC),
            DESTINATION_CHAIN_SELECTOR,
            bob
        );
        
        uint256 balanceBefore = mockUSDC.balanceOf(alice);
        
        // Cancel intent
        intentFi.cancelIntent(intentId);
        
        uint256 balanceAfter = mockUSDC.balanceOf(alice);
        
        vm.stopPrank();
        
        // Check tokens were refunded
        assertEq(balanceAfter - balanceBefore, INTENT_AMOUNT);
        
        // Check intent status
        IntentFi.Intent memory intent = intentFi.getIntentDetails(intentId);
        assertEq(uint8(intent.status), uint8(IntentFi.IntentStatus.CANCELLED));
    }

    function testGetCurrentPrice() public {
        int256 currentPrice = intentFi.getCurrentPrice();
        assertEq(currentPrice, INITIAL_ETH_PRICE);
    }

    function testGetUserIntents() public {
        vm.startPrank(alice);
        mockUSDC.approve(address(intentFi), INTENT_AMOUNT * 2);
        
        // Create two intents
        intentFi.createIntent(
            IntentFi.IntentType.SEND_IF_PRICE_ABOVE,
            3500 * 1e8,
            INTENT_AMOUNT,
            address(mockUSDC),
            DESTINATION_CHAIN_SELECTOR,
            bob
        );
        
        intentFi.createIntent(
            IntentFi.IntentType.SEND_IF_PRICE_BELOW,
            2500 * 1e8,
            INTENT_AMOUNT,
            address(mockUSDC),
            DESTINATION_CHAIN_SELECTOR,
            bob
        );
        
        vm.stopPrank();
        
        uint256[] memory userIntents = intentFi.getUserIntents(alice);
        assertEq(userIntents.length, 2);
        assertEq(userIntents[0], 1);
        assertEq(userIntents[1], 2);
    }

    function test_RevertIf_CreateIntentWithInsufficientBalance() public {
        vm.startPrank(alice);
        
        // Try to create intent without approving tokens
        vm.expectRevert();
        intentFi.createIntent(
            IntentFi.IntentType.SEND_IF_PRICE_ABOVE,
            3500 * 1e8,
            INTENT_AMOUNT,
            address(mockUSDC),
            DESTINATION_CHAIN_SELECTOR,
            bob
        );
        
        vm.stopPrank();
    }

    function test_RevertIf_CreateIntentWithUnallowlistedChain() public {
        vm.startPrank(alice);
        mockUSDC.approve(address(intentFi), INTENT_AMOUNT);
        
        // Try to create intent for unallowlisted chain
        vm.expectRevert();
        intentFi.createIntent(
            IntentFi.IntentType.SEND_IF_PRICE_ABOVE,
            3500 * 1e8,
            INTENT_AMOUNT,
            address(mockUSDC),
            99999, // Invalid chain selector
            bob
        );
        
        vm.stopPrank();
    }

    function testAdminFunctions() public {
        vm.startPrank(owner);
        
        // Test allowlist chain
        intentFi.allowlistDestinationChain(54321, true);
        assertTrue(intentFi.allowlistedDestinationChains(54321));
        
        // Test update CCIP router
        address newRouter = makeAddr("newRouter");
        intentFi.updateCCIPRouter(newRouter);
        assertEq(intentFi.ccipRouterAddress(), newRouter);
        
        // Test update price feed
        MockV3Aggregator newPriceFeed = new MockV3Aggregator(8, 4000 * 1e8);
        intentFi.updatePriceFeed(address(newPriceFeed));
        assertEq(intentFi.getCurrentPrice(), 4000 * 1e8);
        
        vm.stopPrank();
    }
}
