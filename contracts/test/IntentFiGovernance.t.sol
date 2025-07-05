// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Test, console2} from "forge-std/Test.sol";
import {IntentFiGovernance} from "../src/IntentFiGovernance.sol";
import {MockERC20} from "./mocks/MockERC20.sol";

/**
 * @title IntentFiGovernanceTest
 * @notice Comprehensive test suite for IntentFiGovernance contract
 */
contract IntentFiGovernanceTest is Test {
    IntentFiGovernance public governance;
    MockERC20 public governanceToken;
    
    address public owner = makeAddr("owner");
    address public proposer = makeAddr("proposer");
    address public voter1 = makeAddr("voter1");
    address public voter2 = makeAddr("voter2");
    address public emergencyMultisig1 = makeAddr("emergencyMultisig1");
    address public emergencyMultisig2 = makeAddr("emergencyMultisig2");
    address public emergencyMultisig3 = makeAddr("emergencyMultisig3");
    
    // Test target contract for proposals
    TestTarget public testTarget;
    
    uint256 constant PROPOSAL_THRESHOLD = 100000e18; // 100,000 tokens
    uint256 constant VOTING_DELAY = 1 days;
    uint256 constant VOTING_PERIOD = 3 days;
    uint256 constant EXECUTION_DELAY = 2 days;
    
    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed proposer,
        string title,
        uint256 startTime,
        uint256 endTime
    );
    
    event VoteCast(
        uint256 indexed proposalId,
        address indexed voter,
        bool support,
        uint256 weight,
        bool abstain
    );
    
    event ProposalExecuted(uint256 indexed proposalId);
    event ProposalCancelled(uint256 indexed proposalId);

    function setUp() public {
        // Deploy governance token
        governanceToken = new MockERC20("Governance Token", "GOV", 18);
        
        // Deploy test target
        testTarget = new TestTarget();
        
        // Setup emergency multisig addresses
        address[] memory multisigAddresses = new address[](3);
        multisigAddresses[0] = emergencyMultisig1;
        multisigAddresses[1] = emergencyMultisig2;
        multisigAddresses[2] = emergencyMultisig3;
        
        // Deploy governance contract
        vm.prank(owner);
        governance = new IntentFiGovernance(
            address(governanceToken),
            owner,
            multisigAddresses
        );
        
        // Mint tokens to test accounts
        governanceToken.mint(proposer, PROPOSAL_THRESHOLD * 2);
        governanceToken.mint(voter1, 500000e18);
        governanceToken.mint(voter2, 300000e18);
    }

    function testDeployment() public view {
        assertEq(address(governance.governanceToken()), address(governanceToken));
        assertEq(governance.owner(), owner);
        assertTrue(governance.emergencyMultisig(emergencyMultisig1));
        assertTrue(governance.emergencyMultisig(emergencyMultisig2));
        assertTrue(governance.emergencyMultisig(emergencyMultisig3));
        
        // Check initial governance parameters
        (
            uint256 votingDelay,
            uint256 votingPeriod,
            uint256 proposalThreshold,
            uint256 quorumThreshold,
            uint256 executionDelay,
            uint256 minExecutionDelay,
            uint256 maxExecutionDelay
        ) = governance.governanceParams();
        
        assertEq(votingDelay, VOTING_DELAY);
        assertEq(votingPeriod, VOTING_PERIOD);
        assertEq(proposalThreshold, PROPOSAL_THRESHOLD);
        assertEq(quorumThreshold, 400); // 4%
        assertEq(executionDelay, EXECUTION_DELAY);
        assertEq(minExecutionDelay, 1 days);
        assertEq(maxExecutionDelay, 7 days);
    }

    function testCreateProposal() public {
        vm.prank(proposer);
        
        bytes memory callData = abi.encodeWithSignature("setValue(uint256)", 42);
        
        vm.expectEmit(true, true, false, true);
        emit ProposalCreated(1, proposer, "Test Proposal", block.timestamp + VOTING_DELAY, block.timestamp + VOTING_DELAY + VOTING_PERIOD);
        
        uint256 proposalId = governance.propose(
            "Test Proposal",
            "This is a test proposal",
            address(testTarget),
            0,
            callData
        );
        
        assertEq(proposalId, 1);
        assertEq(governance.nextProposalId(), 2);
        
        // Check proposal details
        (
            address proposer_,
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
        
        assertEq(proposer_, proposer);
        assertEq(title, "Test Proposal");
        assertEq(description, "This is a test proposal");
        assertEq(startTime, block.timestamp + VOTING_DELAY);
        assertEq(endTime, block.timestamp + VOTING_DELAY + VOTING_PERIOD);
        assertEq(forVotes, 0);
        assertEq(againstVotes, 0);
        assertEq(abstainVotes, 0);
        assertFalse(executed);
        assertFalse(cancelled);
    }

    function testCreateProposalInsufficientVotingPower() public {
        address lowPowerUser = makeAddr("lowPowerUser");
        governanceToken.mint(lowPowerUser, 1000e18); // Less than threshold
        
        vm.prank(lowPowerUser);
        vm.expectRevert("Insufficient voting power");
        governance.propose(
            "Test Proposal",
            "This should fail",
            address(testTarget),
            0,
            abi.encodeWithSignature("setValue(uint256)", 42)
        );
    }

    function testVoting() public {
        // Create proposal
        vm.prank(proposer);
        uint256 proposalId = governance.propose(
            "Test Proposal",
            "Test voting",
            address(testTarget),
            0,
            abi.encodeWithSignature("setValue(uint256)", 42)
        );
        
        // Fast forward past voting delay
        vm.warp(block.timestamp + VOTING_DELAY + 1);
        
        // Vote for
        vm.prank(voter1);
        vm.expectEmit(true, true, false, true);
        emit VoteCast(proposalId, voter1, true, 500000e18, false);
        governance.castVote(proposalId, true, false);
        
        // Vote against
        vm.prank(voter2);
        governance.castVote(proposalId, false, false);
        
        // Check votes
        (
            ,,,,,
            uint256 forVotes,
            uint256 againstVotes,
            uint256 abstainVotes,,
        ) = governance.getProposalDetails(proposalId);
        
        assertEq(forVotes, 500000e18);
        assertEq(againstVotes, 300000e18);
        assertEq(abstainVotes, 0);
        
        // Check user votes
        (bool hasVoted1, bool support1, uint256 weight1, bool abstain1) = governance.getUserVote(proposalId, voter1);
        assertTrue(hasVoted1);
        assertTrue(support1);
        assertEq(weight1, 500000e18);
        assertFalse(abstain1);
    }

    function testVotingAbstain() public {
        // Create proposal
        vm.prank(proposer);
        uint256 proposalId = governance.propose(
            "Test Proposal",
            "Test abstain voting",
            address(testTarget),
            0,
            abi.encodeWithSignature("setValue(uint256)", 42)
        );
        
        // Fast forward past voting delay
        vm.warp(block.timestamp + VOTING_DELAY + 1);
        
        // Vote abstain
        vm.prank(voter1);
        governance.castVote(proposalId, false, true); // support doesn't matter when abstaining
        
        // Check votes
        (
            ,,,,,
            uint256 forVotes,
            uint256 againstVotes,
            uint256 abstainVotes,,
        ) = governance.getProposalDetails(proposalId);
        
        assertEq(forVotes, 0);
        assertEq(againstVotes, 0);
        assertEq(abstainVotes, 500000e18);
    }

    function testVotingRestrictions() public {
        // Create proposal
        vm.prank(proposer);
        uint256 proposalId = governance.propose(
            "Test Proposal",
            "Test voting restrictions",
            address(testTarget),
            0,
            abi.encodeWithSignature("setValue(uint256)", 42)
        );
        
        // Try to vote before voting starts
        vm.prank(voter1);
        vm.expectRevert("Voting not started");
        governance.castVote(proposalId, true, false);
        
        // Fast forward past voting delay
        vm.warp(block.timestamp + VOTING_DELAY + 1);
        
        // Vote once
        vm.prank(voter1);
        governance.castVote(proposalId, true, false);
        
        // Try to vote again
        vm.prank(voter1);
        vm.expectRevert("Already voted");
        governance.castVote(proposalId, false, false);
        
        // Fast forward past voting period
        vm.warp(block.timestamp + VOTING_PERIOD + 1);
        
        // Try to vote after period ends
        vm.prank(voter2);
        vm.expectRevert("Voting ended");
        governance.castVote(proposalId, true, false);
    }

    function testProposalExecution() public {
        // Create proposal
        vm.prank(proposer);
        uint256 proposalId = governance.propose(
            "Test Proposal",
            "Test execution",
            address(testTarget),
            0,
            abi.encodeWithSignature("setValue(uint256)", 42)
        );
        
        // Fast forward and vote (ensure it passes)
        vm.warp(block.timestamp + VOTING_DELAY + 1);
        vm.prank(voter1);
        governance.castVote(proposalId, true, false);
        vm.prank(voter2);
        governance.castVote(proposalId, true, false);
        
        // Fast forward past voting period
        vm.warp(block.timestamp + VOTING_PERIOD + 1);
        
        // First execution call sets timelock
        governance.executeProposal(proposalId);
        
        // Fast forward past execution delay
        vm.warp(block.timestamp + EXECUTION_DELAY + 1);
        
        // Execute proposal
        vm.expectEmit(true, false, false, false);
        emit ProposalExecuted(proposalId);
        governance.executeProposal(proposalId);
        
        // Check that target was called
        assertEq(testTarget.value(), 42);
        
        // Check proposal is marked as executed
        (,,,,,,,, bool executed,) = governance.getProposalDetails(proposalId);
        assertTrue(executed);
    }

    function testProposalCancellation() public {
        // Create proposal
        vm.prank(proposer);
        uint256 proposalId = governance.propose(
            "Test Proposal",
            "Test cancellation",
            address(testTarget),
            0,
            abi.encodeWithSignature("setValue(uint256)", 42)
        );
        
        // Cancel by proposer
        vm.prank(proposer);
        vm.expectEmit(true, false, false, false);
        emit ProposalCancelled(proposalId);
        governance.cancelProposal(proposalId);
        
        // Check proposal is cancelled
        (,,,,,,,, bool executed, bool cancelled) = governance.getProposalDetails(proposalId);
        assertFalse(executed);
        assertTrue(cancelled);
    }

    function testDelegation() public {
        address delegator = makeAddr("delegator");
        address delegatee = makeAddr("delegatee");
        
        governanceToken.mint(delegator, 1000000e18);
        
        // Check initial voting power
        assertEq(governance.getVotingPower(delegator), 1000000e18);
        assertEq(governance.getVotingPower(delegatee), 0);
        
        // Delegate
        vm.prank(delegator);
        governance.delegate(delegatee);
        
        // Check voting power after delegation
        assertEq(governance.getVotingPower(delegator), 1000000e18); // Still has token balance
        assertEq(governance.getVotingPower(delegatee), 1000000e18); // Gets delegated votes
        assertEq(governance.delegatedVotes(delegatee), 1000000e18);
        assertEq(governance.delegates(delegator), delegatee);
    }

    function testEmergencyPause() public {
        // Test emergency pause
        vm.prank(emergencyMultisig1);
        governance.emergencyPause();
        
        (,,,,,bool emergencyPauseEnabled) = governance.protocolParams();
        assertTrue(emergencyPauseEnabled);
        
        // Test emergency unpause
        vm.prank(emergencyMultisig2);
        governance.emergencyUnpause();
        
        (,,,,,emergencyPauseEnabled) = governance.protocolParams();
        assertFalse(emergencyPauseEnabled);
    }

    function testEmergencyPauseUnauthorized() public {
        address unauthorized = makeAddr("unauthorized");
        
        vm.prank(unauthorized);
        vm.expectRevert("Not emergency multisig");
        governance.emergencyPause();
    }

    function testGetVotingPower() public {
        address user = makeAddr("user");
        address delegatee = makeAddr("delegatee");
        
        governanceToken.mint(user, 1000000e18);
        governanceToken.mint(delegatee, 500000e18);
        
        // Initial voting power is token balance
        assertEq(governance.getVotingPower(user), 1000000e18);
        assertEq(governance.getVotingPower(delegatee), 500000e18);
        
        // Delegate from user to delegatee
        vm.prank(user);
        governance.delegate(delegatee);
        
        // Delegatee now has own balance + delegated votes
        assertEq(governance.getVotingPower(delegatee), 1500000e18);
        assertEq(governance.getVotingPower(user), 1000000e18); // Still has own balance
    }

    function testProposalThresholdCheck() public {
        // Test with exact threshold
        address exactThresholdUser = makeAddr("exactThresholdUser");
        governanceToken.mint(exactThresholdUser, PROPOSAL_THRESHOLD);
        
        vm.prank(exactThresholdUser);
        uint256 proposalId = governance.propose(
            "Exact Threshold Proposal",
            "Test with exact threshold",
            address(testTarget),
            0,
            abi.encodeWithSignature("setValue(uint256)", 100)
        );
        
        assertEq(proposalId, 1);
    }

    function testQuorumCheck() public {
        // Create proposal that should fail due to insufficient quorum
        vm.prank(proposer);
        uint256 proposalId = governance.propose(
            "Low Quorum Proposal",
            "Test quorum failure",
            address(testTarget),
            0,
            abi.encodeWithSignature("setValue(uint256)", 42)
        );
        
        // Fast forward and have only small votes
        vm.warp(block.timestamp + VOTING_DELAY + 1);
        
        address smallVoter = makeAddr("smallVoter");
        governanceToken.mint(smallVoter, 1000e18); // Very small amount
        
        vm.prank(smallVoter);
        governance.castVote(proposalId, true, false);
        
        // Fast forward past voting period
        vm.warp(block.timestamp + VOTING_PERIOD + 1);
        
        // Try to execute - should fail due to insufficient quorum
        vm.expectRevert("Proposal did not pass");
        governance.executeProposal(proposalId);
    }
}

/**
 * @title TestTarget
 * @notice Simple target contract for testing proposal execution
 */
contract TestTarget {
    uint256 public value;
    
    function setValue(uint256 _value) external {
        value = _value;
    }
}
