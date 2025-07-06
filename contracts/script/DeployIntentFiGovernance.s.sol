// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Script, console2} from "forge-std/Script.sol";
import {IntentFiGovernance} from "../src/IntentFiGovernance.sol";

/**
 * @title DeployIntentFiGovernance
 * @notice Deployment script for IntentFiGovernance contract
 */
contract DeployIntentFiGovernance is Script {
    // Chain configurations
    struct ChainConfig {
        address governanceToken;
        address owner;
        address[] emergencyMultisig;
        string networkName;
    }

    mapping(uint256 => ChainConfig) public chainConfigs;

    function setUp() public {
        // Ethereum Mainnet configuration
        address[] memory mainnetMultisig = new address[](5);
        mainnetMultisig[0] = 0x1111111111111111111111111111111111111111; // Replace with actual addresses
        mainnetMultisig[1] = 0x2222222222222222222222222222222222222222;
        mainnetMultisig[2] = 0x3333333333333333333333333333333333333333;
        mainnetMultisig[3] = 0x4444444444444444444444444444444444444444;
        mainnetMultisig[4] = 0x5555555555555555555555555555555555555555;

        chainConfigs[1] = ChainConfig({
            governanceToken: address(0), // To be deployed or set
            owner: 0xA1B2c3d4e5f6789012345678901234567890ABcD, // Replace with actual owner
            emergencyMultisig: mainnetMultisig,
            networkName: "Ethereum Mainnet"
        });

        // Sepolia configuration
        address[] memory sepoliaMultisig = new address[](3);
        sepoliaMultisig[0] = 0x1111111111111111111111111111111111111111; // Replace with actual addresses
        sepoliaMultisig[1] = 0x2222222222222222222222222222222222222222;
        sepoliaMultisig[2] = 0x3333333333333333333333333333333333333333;

        chainConfigs[11155111] = ChainConfig({
            governanceToken: address(0), // To be deployed or set
            owner: 0xA1B2c3d4e5f6789012345678901234567890ABcD, // Replace with actual owner
            emergencyMultisig: sepoliaMultisig,
            networkName: "Sepolia Testnet"
        });

        // Polygon configuration
        address[] memory polygonMultisig = new address[](3);
        polygonMultisig[0] = 0x1111111111111111111111111111111111111111; // Replace with actual addresses
        polygonMultisig[1] = 0x2222222222222222222222222222222222222222;
        polygonMultisig[2] = 0x3333333333333333333333333333333333333333;

        chainConfigs[137] = ChainConfig({
            governanceToken: address(0), // To be deployed or set
            owner: 0xA1B2c3d4e5f6789012345678901234567890ABcD, // Replace with actual owner
            emergencyMultisig: polygonMultisig,
            networkName: "Polygon Mainnet"
        });

        // Base configuration
        address[] memory baseMultisig = new address[](3);
        baseMultisig[0] = 0x1111111111111111111111111111111111111111; // Replace with actual addresses
        baseMultisig[1] = 0x2222222222222222222222222222222222222222;
        baseMultisig[2] = 0x3333333333333333333333333333333333333333;

        chainConfigs[8453] = ChainConfig({
            governanceToken: address(0), // To be deployed or set
            owner: 0xA1B2c3d4e5f6789012345678901234567890ABcD, // Replace with actual owner
            emergencyMultisig: baseMultisig,
            networkName: "Base Mainnet"
        });

        // Arbitrum configuration
        address[] memory arbitrumMultisig = new address[](3);
        arbitrumMultisig[0] = 0x1111111111111111111111111111111111111111; // Replace with actual addresses
        arbitrumMultisig[1] = 0x2222222222222222222222222222222222222222;
        arbitrumMultisig[2] = 0x3333333333333333333333333333333333333333;

        chainConfigs[42161] = ChainConfig({
            governanceToken: address(0), // To be deployed or set
            owner: 0xA1B2c3d4e5f6789012345678901234567890ABcD, // Replace with actual owner
            emergencyMultisig: arbitrumMultisig,
            networkName: "Arbitrum One"
        });
    }

    // Helper function to extract substring
    function substring(string memory str, uint256 startIndex, uint256 endIndex) internal pure returns (string memory) {
        bytes memory strBytes = bytes(str);
        bytes memory result = new bytes(endIndex - startIndex);
        for (uint256 i = startIndex; i < endIndex; i++) {
            result[i - startIndex] = strBytes[i];
        }
        return string(result);
    }

    function run() external {
        // Get private key from environment
        string memory privateKeyEnv = vm.envString("PRIVATE_KEY");
        uint256 deployerPrivateKey;

        // Handle private key with or without 0x prefix
        if (bytes(privateKeyEnv).length > 2 && bytes(privateKeyEnv)[0] == "0" && bytes(privateKeyEnv)[1] == "x") {
            // Already has 0x prefix
            deployerPrivateKey = vm.parseUint(privateKeyEnv);
        } else {
            // Add 0x prefix for hex parsing
            string memory prefixedKey = string.concat("0x", privateKeyEnv);
            deployerPrivateKey = vm.parseUint(prefixedKey);
        }

        uint256 chainId = block.chainid;

        ChainConfig memory config = chainConfigs[chainId];
        require(bytes(config.networkName).length > 0, "Chain not supported");

        // Get governance token address from environment or deploy
        address governanceTokenAddress = vm.envOr("GOVERNANCE_TOKEN_ADDRESS", address(0));
        if (governanceTokenAddress != address(0)) {
            config.governanceToken = governanceTokenAddress;
        }

        // Get owner from environment if set
        address ownerAddress = vm.envOr("GOVERNANCE_OWNER", config.owner);
        if (ownerAddress != address(0)) {
            config.owner = ownerAddress;
        }

        require(config.governanceToken != address(0), "Governance token address not set");
        require(config.owner != address(0), "Owner address not set");

        vm.startBroadcast(deployerPrivateKey);

        console2.log("=== Deploying IntentFiGovernance ===");
        console2.log("Network:", config.networkName);
        console2.log("Chain ID:", chainId);
        console2.log("Governance Token:", config.governanceToken);
        console2.log("Owner:", config.owner);
        console2.log("Emergency Multisig Members:", config.emergencyMultisig.length);

        for (uint256 i = 0; i < config.emergencyMultisig.length; i++) {
            console2.log("  Multisig", i + 1, ":", config.emergencyMultisig[i]);
        }

        // Deploy IntentFiGovernance
        IntentFiGovernance governance =
            new IntentFiGovernance(config.governanceToken, config.owner, config.emergencyMultisig);

        console2.log("IntentFiGovernance deployed at:", address(governance));

        // Verify deployment
        _verifyDeployment(governance, config);

        vm.stopBroadcast();

        console2.log("=== Deployment Complete ===");
        console2.log("Contract Address:", address(governance));
        console2.log("Verification command:");
        console2.log(
            string.concat(
                "forge verify-contract ",
                vm.toString(address(governance)),
                " src/IntentFiGovernance.sol:IntentFiGovernance --chain-id ",
                vm.toString(chainId),
                " --constructor-args ",
                vm.toString(abi.encode(config.governanceToken, config.owner, config.emergencyMultisig))
            )
        );

        console2.log("\n=== Post-Deployment Setup ===");
        console2.log("1. Verify governance token integration");
        console2.log("2. Test emergency multisig functionality");
        console2.log("3. Create initial governance proposals");
        console2.log("4. Set up monitoring and alerts");
    }

    function _verifyDeployment(IntentFiGovernance governance, ChainConfig memory config) internal view {
        console2.log("Verifying deployment...");

        // Verify governance token
        require(address(governance.governanceToken()) == config.governanceToken, "Governance token mismatch");

        // Verify owner
        require(governance.owner() == config.owner, "Owner mismatch");

        // Verify emergency multisig
        for (uint256 i = 0; i < config.emergencyMultisig.length; i++) {
            require(governance.emergencyMultisig(config.emergencyMultisig[i]), "Emergency multisig not set");
        }

        // Verify initial parameters
        (
            uint256 votingDelay,
            uint256 votingPeriod,
            uint256 proposalThreshold,
            uint256 quorumThreshold,
            uint256 executionDelay,
            uint256 minExecutionDelay,
            uint256 maxExecutionDelay
        ) = governance.governanceParams();

        require(votingDelay == 1 days, "Voting delay incorrect");
        require(votingPeriod == 3 days, "Voting period incorrect");
        require(proposalThreshold == 100000e18, "Proposal threshold incorrect");
        require(quorumThreshold == 400, "Quorum threshold incorrect");
        require(executionDelay == 2 days, "Execution delay incorrect");
        require(minExecutionDelay == 1 days, "Min execution delay incorrect");
        require(maxExecutionDelay == 7 days, "Max execution delay incorrect");

        console2.log("Deployment verification passed");
    }

    /**
     * @notice Deploy with custom parameters for testing
     */
    function deployForTesting() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");

        vm.startBroadcast(deployerPrivateKey);

        console2.log("=== Deploying IntentFiGovernance for Testing ===");

        // Deploy mock governance token for testing
        MockGovernanceToken mockToken = new MockGovernanceToken();
        console2.log("Mock Governance Token deployed at:", address(mockToken));

        // Use deployer as owner for testing
        address testOwner = vm.addr(deployerPrivateKey);

        // Create test multisig addresses
        address[] memory testMultisig = new address[](3);
        testMultisig[0] = makeAddr("testMultisig1");
        testMultisig[1] = makeAddr("testMultisig2");
        testMultisig[2] = makeAddr("testMultisig3");

        IntentFiGovernance governance = new IntentFiGovernance(address(mockToken), testOwner, testMultisig);

        console2.log("Test IntentFiGovernance deployed at:", address(governance));

        // Mint some test tokens
        mockToken.mint(testOwner, 1000000e18);
        console2.log("Minted test tokens to:", testOwner);

        vm.stopBroadcast();

        console2.log("=== Test Deployment Complete ===");
    }

    /**
     * @notice Deploy governance token separately if needed
     */
    function deployGovernanceToken() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");

        vm.startBroadcast(deployerPrivateKey);

        console2.log("=== Deploying Governance Token ===");

        MockGovernanceToken governanceToken = new MockGovernanceToken();

        console2.log("Governance Token deployed at:", address(governanceToken));
        console2.log("Token Name:", governanceToken.name());
        console2.log("Token Symbol:", governanceToken.symbol());
        console2.log("Token Decimals:", governanceToken.decimals());

        vm.stopBroadcast();
    }

    function makeAddr(string memory name) internal pure override returns (address) {
        return address(uint160(uint256(keccak256(abi.encodePacked(name)))));
    }
}

/**
 * @title MockGovernanceToken
 * @notice Simple ERC20 token for testing governance
 */
contract MockGovernanceToken {
    string public name = "IntentFi Governance Token";
    string public symbol = "IFG";
    uint8 public decimals = 18;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    uint256 public totalSupply;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
        totalSupply += amount;
        emit Transfer(address(0), to, amount);
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        emit Transfer(msg.sender, to, amount);
        return true;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        require(balanceOf[from] >= amount, "Insufficient balance");
        require(allowance[from][msg.sender] >= amount, "Insufficient allowance");

        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        allowance[from][msg.sender] -= amount;

        emit Transfer(from, to, amount);
        return true;
    }
}
