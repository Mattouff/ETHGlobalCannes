// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title IntentFiGovernance
 * @notice Governance contract for managing IntentFi protocol parameters
 * @dev Handles voting, proposals, and parameter updates for the IntentFi ecosystem
 */
contract IntentFiGovernance is Ownable, ReentrancyGuard {
    
    // Governance token interface
    IERC20 public immutable governanceToken;
    
    // Proposal structure
    struct Proposal {
        uint256 id;
        address proposer;
        string title;
        string description;
        bytes callData;
        address target;
        uint256 value;
        uint256 startTime;
        uint256 endTime;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 abstainVotes;
        bool executed;
        bool cancelled;
        mapping(address => Vote) votes;
        mapping(address => bool) hasVoted;
    }

    // Vote structure
    struct Vote {
        bool support;      // true for yes, false for no
        uint256 weight;    // voting power used
        bool abstain;      // abstain vote
    }

    // Governance parameters
    struct GovernanceParams {
        uint256 votingDelay;           // Delay before voting starts (blocks)
        uint256 votingPeriod;          // Voting period duration (blocks)
        uint256 proposalThreshold;     // Minimum tokens to create proposal
        uint256 quorumThreshold;       // Minimum participation for valid vote
        uint256 executionDelay;        // Delay before execution (timelock)
        uint256 minExecutionDelay;     // Minimum execution delay
        uint256 maxExecutionDelay;     // Maximum execution delay
    }

    // Protocol parameters that can be governed
    struct ProtocolParams {
        uint256 maxIntentDuration;     // Maximum intent duration
        uint256 minIntentAmount;       // Minimum intent amount
        uint256 protocolFeeRate;       // Protocol fee rate (basis points)
        uint256 maxSlippageTolerance;  // Maximum allowed slippage
        uint256 emergencyPauseDuration; // Emergency pause duration
        bool emergencyPauseEnabled;    // Emergency pause status
    }

    // Events
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
    
    event ParameterUpdated(string indexed parameter, uint256 oldValue, uint256 newValue);
    event EmergencyPauseToggled(bool enabled);

    // State variables
    mapping(uint256 => Proposal) public proposals;
    mapping(address => uint256) public votingPower;
    mapping(address => uint256) public delegatedVotes;
    mapping(address => address) public delegates;
    
    uint256 public nextProposalId = 1;
    GovernanceParams public governanceParams;
    ProtocolParams public protocolParams;
    
    // Multisig addresses for emergency actions
    mapping(address => bool) public emergencyMultisig;
    uint256 public emergencyThreshold = 3; // Require 3 signatures
    
    // Timelock for executed proposals
    mapping(uint256 => uint256) public proposalExecutionTime;

    constructor(
        address _governanceToken,
        address _owner,
        address[] memory _emergencyMultisig
    ) Ownable(_owner) {
        governanceToken = IERC20(_governanceToken);
        
        // Initialize governance parameters
        governanceParams = GovernanceParams({
            votingDelay: 1 days,
            votingPeriod: 3 days,
            proposalThreshold: 100000e18, // 100,000 tokens
            quorumThreshold: 400, // 4% (in basis points)
            executionDelay: 2 days,
            minExecutionDelay: 1 days,
            maxExecutionDelay: 7 days
        });

        // Initialize protocol parameters
        protocolParams = ProtocolParams({
            maxIntentDuration: 365 days,
            minIntentAmount: 1e6, // 1 USDC
            protocolFeeRate: 30, // 0.3%
            maxSlippageTolerance: 1000, // 10%
            emergencyPauseDuration: 7 days,
            emergencyPauseEnabled: false
        });

        // Set emergency multisig
        for (uint256 i = 0; i < _emergencyMultisig.length; i++) {
            emergencyMultisig[_emergencyMultisig[i]] = true;
        }
    }

    /**
     * @notice Create a new governance proposal
     * @param title Proposal title
     * @param description Proposal description
     * @param target Target contract address
     * @param value ETH value to send
     * @param callData Function call data
     */
    function propose(
        string memory title,
        string memory description,
        address target,
        uint256 value,
        bytes memory callData
    ) external returns (uint256 proposalId) {
        require(
            getVotingPower(msg.sender) >= governanceParams.proposalThreshold,
            "Insufficient voting power"
        );

        proposalId = nextProposalId++;
        Proposal storage proposal = proposals[proposalId];
        
        proposal.id = proposalId;
        proposal.proposer = msg.sender;
        proposal.title = title;
        proposal.description = description;
        proposal.target = target;
        proposal.value = value;
        proposal.callData = callData;
        proposal.startTime = block.timestamp + governanceParams.votingDelay;
        proposal.endTime = proposal.startTime + governanceParams.votingPeriod;

        emit ProposalCreated(
            proposalId,
            msg.sender,
            title,
            proposal.startTime,
            proposal.endTime
        );
    }

    /**
     * @notice Cast a vote on a proposal
     * @param proposalId ID of the proposal
     * @param support True for yes, false for no
     * @param abstain True for abstain vote
     */
    function castVote(
        uint256 proposalId,
        bool support,
        bool abstain
    ) external {
        Proposal storage proposal = proposals[proposalId];
        require(proposal.id != 0, "Proposal does not exist");
        require(block.timestamp >= proposal.startTime, "Voting not started");
        require(block.timestamp <= proposal.endTime, "Voting ended");
        require(!proposal.hasVoted[msg.sender], "Already voted");

        uint256 weight = getVotingPower(msg.sender);
        require(weight > 0, "No voting power");

        proposal.hasVoted[msg.sender] = true;
        proposal.votes[msg.sender] = Vote({
            support: support,
            weight: weight,
            abstain: abstain
        });

        if (abstain) {
            proposal.abstainVotes += weight;
        } else if (support) {
            proposal.forVotes += weight;
        } else {
            proposal.againstVotes += weight;
        }

        emit VoteCast(proposalId, msg.sender, support, weight, abstain);
    }

    /**
     * @notice Execute a passed proposal
     * @param proposalId ID of the proposal to execute
     */
    function executeProposal(uint256 proposalId) external nonReentrant {
        Proposal storage proposal = proposals[proposalId];
        require(proposal.id != 0, "Proposal does not exist");
        require(block.timestamp > proposal.endTime, "Voting still active");
        require(!proposal.executed, "Already executed");
        require(!proposal.cancelled, "Proposal cancelled");

        // Check if proposal passed
        require(_isProposalPassed(proposal), "Proposal did not pass");

        // Check timelock
        if (proposalExecutionTime[proposalId] == 0) {
            proposalExecutionTime[proposalId] = block.timestamp + governanceParams.executionDelay;
            return;
        }

        require(
            block.timestamp >= proposalExecutionTime[proposalId],
            "Execution delay not met"
        );

        proposal.executed = true;

        // Execute the proposal
        (bool success, ) = proposal.target.call{value: proposal.value}(proposal.callData);
        require(success, "Proposal execution failed");

        emit ProposalExecuted(proposalId);
    }

    /**
     * @notice Cancel a proposal (admin or proposer only)
     * @param proposalId ID of the proposal to cancel
     */
    function cancelProposal(uint256 proposalId) external {
        Proposal storage proposal = proposals[proposalId];
        require(proposal.id != 0, "Proposal does not exist");
        require(
            msg.sender == proposal.proposer || msg.sender == owner(),
            "Not authorized"
        );
        require(!proposal.executed, "Already executed");

        proposal.cancelled = true;
        emit ProposalCancelled(proposalId);
    }

    /**
     * @notice Delegate voting power to another address
     * @param delegatee Address to delegate to
     */
    function delegate(address delegatee) external {
        address currentDelegate = delegates[msg.sender];
        uint256 delegatorBalance = governanceToken.balanceOf(msg.sender);

        delegates[msg.sender] = delegatee;

        // Remove delegation from current delegate
        if (currentDelegate != address(0)) {
            delegatedVotes[currentDelegate] -= delegatorBalance;
        }

        // Add delegation to new delegate
        if (delegatee != address(0)) {
            delegatedVotes[delegatee] += delegatorBalance;
        }
    }

    /**
     * @notice Emergency pause (multisig only)
     */
    function emergencyPause() external {
        require(emergencyMultisig[msg.sender], "Not emergency multisig");
        require(!protocolParams.emergencyPauseEnabled, "Already paused");

        protocolParams.emergencyPauseEnabled = true;
        emit EmergencyPauseToggled(true);
    }

    /**
     * @notice Emergency unpause (multisig only)
     */
    function emergencyUnpause() external {
        require(emergencyMultisig[msg.sender], "Not emergency multisig");
        require(protocolParams.emergencyPauseEnabled, "Not paused");

        protocolParams.emergencyPauseEnabled = false;
        emit EmergencyPauseToggled(false);
    }

    /**
     * @notice Update governance parameters (internal)
     * @param newParams New governance parameters
     */
    function _updateGovernanceParams(GovernanceParams memory newParams) internal {
        require(
            newParams.minExecutionDelay <= newParams.executionDelay &&
            newParams.executionDelay <= newParams.maxExecutionDelay,
            "Invalid execution delay"
        );
        
        governanceParams = newParams;
    }

    /**
     * @notice Update protocol parameters (internal)
     * @param newParams New protocol parameters
     */
    function _updateProtocolParams(ProtocolParams memory newParams) internal {
        protocolParams = newParams;
    }

    /**
     * @notice Get voting power for an address
     * @param account Address to check
     * @return votingPower Total voting power
     */
    function getVotingPower(address account) public view returns (uint256) {
        return governanceToken.balanceOf(account) + delegatedVotes[account];
    }

    /**
     * @notice Check if a proposal passed
     * @param proposal Proposal to check
     * @return passed Whether the proposal passed
     */
    function _isProposalPassed(Proposal storage proposal) internal view returns (bool passed) {
        uint256 totalVotes = proposal.forVotes + proposal.againstVotes + proposal.abstainVotes;
        uint256 totalSupply = governanceToken.totalSupply();
        
        // Check quorum
        if (totalVotes * 10000 < totalSupply * governanceParams.quorumThreshold) {
            return false;
        }

        // Check majority
        return proposal.forVotes > proposal.againstVotes;
    }

    /**
     * @notice Get proposal details
     * @param proposalId Proposal ID
     * @return proposer Proposer address
     * @return title Proposal title
     * @return description Proposal description
     * @return startTime Voting start time
     * @return endTime Voting end time
     * @return forVotes For votes
     * @return againstVotes Against votes
     * @return abstainVotes Abstain votes
     * @return executed Whether executed
     * @return cancelled Whether cancelled
     */
    function getProposalDetails(uint256 proposalId) 
        external 
        view 
        returns (
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
        )
    {
        Proposal storage proposal = proposals[proposalId];
        return (
            proposal.proposer,
            proposal.title,
            proposal.description,
            proposal.startTime,
            proposal.endTime,
            proposal.forVotes,
            proposal.againstVotes,
            proposal.abstainVotes,
            proposal.executed,
            proposal.cancelled
        );
    }

    /**
     * @notice Get user's vote on a proposal
     * @param proposalId Proposal ID
     * @param voter Voter address
     * @return hasVoted Whether user voted
     * @return support Vote direction
     * @return weight Vote weight
     * @return abstain Whether abstained
     */
    function getUserVote(uint256 proposalId, address voter)
        external
        view
        returns (bool hasVoted, bool support, uint256 weight, bool abstain)
    {
        Proposal storage proposal = proposals[proposalId];
        hasVoted = proposal.hasVoted[voter];
        if (hasVoted) {
            Vote storage vote = proposal.votes[voter];
            support = vote.support;
            weight = vote.weight;
            abstain = vote.abstain;
        }
    }
}
