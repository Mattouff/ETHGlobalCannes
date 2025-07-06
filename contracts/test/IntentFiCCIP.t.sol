// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Test, console2} from "forge-std/Test.sol";
import {IntentFi} from "../src/IntentFi.sol";
import {IntentFiCCIP} from "../src/IntentFiCCIP.sol";
import {MockV3Aggregator} from "./mocks/MockV3Aggregator.sol";
import {MockERC20} from "./mocks/MockERC20.sol";
import {MockCCIPRouter} from "./mocks/MockCCIPRouter.sol";

contract IntentFiCCIPTest is Test {
    IntentFiCCIP public intentFiCCIP;
    MockV3Aggregator public mockPriceFeed;
    MockERC20 public mockUSDC;
    MockERC20 public mockLINK;
    MockCCIPRouter public mockCCIPRouter;
    
    address public alice = makeAddr("alice");
    address public bob = makeAddr("bob");
    address public owner = makeAddr("owner");
    
    uint64 public constant DESTINATION_CHAIN_SELECTOR = 10344971235874465080; // Base Sepolia
    int256 public constant INITIAL_ETH_PRICE = 3000 * 1e8; // $3000 with 8 decimals
    uint256 public constant INTENT_AMOUNT = 50e6; // 50 USDC (6 decimals)
    uint256 public constant LINK_AMOUNT = 10e18; // 10 LINK for fees
    
    event CCIPMessageSent(
        bytes32 indexed messageId,
        uint64 indexed destinationChainSelector,
        address receiver,
        uint256 amount,
        address token
    );

    function setUp() public {
        vm.startPrank(owner);
        
        // Deploy mocks
        mockPriceFeed = new MockV3Aggregator(8, INITIAL_ETH_PRICE);
        mockUSDC = new MockERC20("USD Coin", "USDC", 6);
        mockLINK = new MockERC20("Chainlink Token", "LINK", 18);
        mockCCIPRouter = new MockCCIPRouter();
        
        // Deploy IntentFiCCIP
        intentFiCCIP = new IntentFiCCIP(
            address(mockPriceFeed),
            address(mockCCIPRouter),
            address(mockLINK)
        );
        
        // Setup allowlisted chains
        intentFiCCIP.allowlistDestinationChain(DESTINATION_CHAIN_SELECTOR, true);
        
        vm.stopPrank();
        
        // Give Alice some tokens and LINK
        vm.startPrank(alice);
        mockUSDC.mint(alice, 1000e6); // 1000 USDC
        mockLINK.mint(alice, 100e18); // 100 LINK
        vm.deal(alice, 10 ether);
        vm.stopPrank();
        
        // Give contract some LINK for fees
        vm.startPrank(alice);
        mockLINK.approve(address(intentFiCCIP), LINK_AMOUNT);
        intentFiCCIP.fundLINK(LINK_AMOUNT);
        vm.stopPrank();
    }

    function testFundLINK() public {
        uint256 initialBalance = intentFiCCIP.getLINKBalance();
        
        vm.startPrank(alice);
        mockLINK.approve(address(intentFiCCIP), LINK_AMOUNT);
        
        intentFiCCIP.fundLINK(LINK_AMOUNT);
        
        uint256 finalBalance = intentFiCCIP.getLINKBalance();
        assertEq(finalBalance - initialBalance, LINK_AMOUNT);
        vm.stopPrank();
    }

    function testWithdrawLINK() public {
        uint256 withdrawAmount = 5e18; // 5 LINK
        uint256 initialBalance = mockLINK.balanceOf(owner);
        
        vm.prank(owner);
        intentFiCCIP.withdrawLINK(owner, withdrawAmount);
        
        uint256 finalBalance = mockLINK.balanceOf(owner);
        assertEq(finalBalance - initialBalance, withdrawAmount);
    }

    function testCreateIntentWithCCIP() public {
        vm.startPrank(alice);
        
        // Approve USDC transfer
        mockUSDC.approve(address(intentFiCCIP), INTENT_AMOUNT);
        
        // Create intent: Send 50 USDC if ETH > $3500
        uint256 intentId = intentFiCCIP.createIntent(
            IntentFi.IntentType.SEND_IF_PRICE_ABOVE,
            3500 * 1e8, // $3500 trigger
            INTENT_AMOUNT,
            address(mockUSDC),
            DESTINATION_CHAIN_SELECTOR,
            bob
        );
        
        vm.stopPrank();
        
        assertEq(intentId, 1);
        assertEq(mockUSDC.balanceOf(address(intentFiCCIP)), INTENT_AMOUNT);
    }

    function testCCIPSendSimulation() public {
        // Create intent first
        vm.startPrank(alice);
        mockUSDC.approve(address(intentFiCCIP), INTENT_AMOUNT);
        uint256 intentId = intentFiCCIP.createIntent(
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
        
        // Execute intent (simulate Chainlink Automation call)
        (bool upkeepNeeded, bytes memory performData) = intentFiCCIP.checkUpkeep("");
        assertTrue(upkeepNeeded);
        intentFiCCIP.performUpkeep(performData);
        
        // Check intent status
        IntentFi.Intent memory intent = intentFiCCIP.getIntentDetails(intentId);
        assertEq(uint8(intent.status), uint8(IntentFi.IntentStatus.EXECUTED));
    }

    function testGetCCIPRouter() public {
        address router = intentFiCCIP.getCCIPRouter();
        assertEq(router, address(mockCCIPRouter));
    }

    function testGetLINKToken() public {
        address linkToken = intentFiCCIP.getLINKToken();
        assertEq(linkToken, address(mockLINK));
    }

    function testCrossChainIntentExecution() public {
        // Create intent
        vm.startPrank(alice);
        mockUSDC.approve(address(intentFiCCIP), INTENT_AMOUNT);
        uint256 intentId = intentFiCCIP.createIntent(
            IntentFi.IntentType.SEND_IF_PRICE_ABOVE,
            3500 * 1e8,
            INTENT_AMOUNT,
            address(mockUSDC),
            DESTINATION_CHAIN_SELECTOR,
            bob
        );
        vm.stopPrank();
        
        // Trigger price condition
        mockPriceFeed.updateAnswer(3600 * 1e8);
        
        // Check that checkUpkeep detects the ready intent
        (bool upkeepNeeded, bytes memory performData) = intentFiCCIP.checkUpkeep("");
        assertTrue(upkeepNeeded);
        
        uint256[] memory intentIds = abi.decode(performData, (uint256[]));
        assertEq(intentIds.length, 1);
        assertEq(intentIds[0], intentId);
        
        // Perform upkeep (simulate Chainlink Automation)
        intentFiCCIP.performUpkeep(performData);
        
        // Verify intent was executed
        IntentFi.Intent memory intent = intentFiCCIP.getIntentDetails(intentId);
        assertEq(uint8(intent.status), uint8(IntentFi.IntentStatus.EXECUTED));
    }

    function testRevertIf_WithdrawLINKNotOwner() public {
        vm.prank(alice);
        vm.expectRevert();
        intentFiCCIP.withdrawLINK(alice, 1e18);
    }

    function testRevertIf_InsufficientLINKBalance() public {
        // Try to withdraw more LINK than available
        uint256 availableBalance = intentFiCCIP.getLINKBalance();
        
        vm.prank(owner);
        vm.expectRevert();
        intentFiCCIP.withdrawLINK(owner, availableBalance + 1e18);
    }
}
