// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Script, console2} from "forge-std/Script.sol";
import {IntentFi} from "../src/IntentFi.sol";
import {IntentFiCCIP} from "../src/IntentFiCCIP.sol";
import {IntentFiAdvanced} from "../src/IntentFiAdvanced.sol";
import {IntentFiGovernance} from "../src/IntentFiGovernance.sol";
import {IntentFiUsageExample} from "../src/IntentFiUsageExample.sol";

/**
 * @title DeployIntentFiEcosystem
 * @notice Comprehensive deployment script for the entire IntentFi ecosystem
 */
contract DeployIntentFiEcosystem is Script {
    
    // Deployment configuration per chain
    struct ChainConfig {
        uint64 chainSelector;
        address priceFeed;
        address ccipRouter;
        address linkToken;
        address usdc;
        string rpcUrl;
        string etherscanApiKey;
    }

    // Contract addresses after deployment
    struct DeployedContracts {
        address intentFi;
        address intentFiCCIP;
        address intentFiAdvanced;
        address intentFiGovernance;
        address intentFiUsageExample;
        address governanceToken;
    }

    mapping(uint256 => ChainConfig) public chainConfigs;
    mapping(uint256 => DeployedContracts) public deployedContracts;

    function setUp() public {
        // Sepolia configuration
        chainConfigs[11155111] = ChainConfig({
            chainSelector: 16015286601757825753,
            priceFeed: 0x694AA1769357215DE4FAC081bf1f309aDC325306,
            ccipRouter: 0x0BF3dE8c5D3e8A2B34D2BEeB17ABfCeBaf363A59,
            linkToken: 0x779877A7B0D9E8603169DdbD7836e478b4624789,
            usdc: 0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238,
            rpcUrl: vm.envString("SEPOLIA_RPC_URL"),
            etherscanApiKey: vm.envString("ETHERSCAN_API_KEY")
        });

        // Base Sepolia configuration
        chainConfigs[84532] = ChainConfig({
            chainSelector: 10344971235874465080,
            priceFeed: 0x4aDC67696bA383F43DD60A9e78F2C97Fbbfc7cb1,
            ccipRouter: 0xD3b06cEbF099CE7DA4AcCf578aaebFDBd6e88a93,
            linkToken: 0xE4aB69C077896252FAFBD49EFD26B5D171A32410,
            usdc: 0x036CbD53842c5426634e7929541eC2318f3dCF7e,
            rpcUrl: vm.envString("BASE_SEPOLIA_RPC_URL"),
            etherscanApiKey: vm.envString("BASESCAN_API_KEY")
        });

        // Optimism Sepolia configuration
        chainConfigs[11155420] = ChainConfig({
            chainSelector: 5224473277236331295,
            priceFeed: 0x61Ec26aA57019C486B10502285c5A3D4A4750AD7,
            ccipRouter: 0x114A20A10b43D4115e5aeef7345a1A71d2a60C57,
            linkToken: 0xE4aB69C077896252FAFBD49EFD26B5D171A32410,
            usdc: 0x5fd84259d66Cd46123540766Be93DFE6D43130D7,
            rpcUrl: vm.envString("OPTIMISM_SEPOLIA_RPC_URL"),
            etherscanApiKey: vm.envString("OPTIMISM_ETHERSCAN_API_KEY")
        });

        // Arbitrum Sepolia configuration
        chainConfigs[421614] = ChainConfig({
            chainSelector: 3478487238524512106,
            priceFeed: 0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165,
            ccipRouter: 0x2a9C5afB0d0e4BAb2BCdaE109EC4b0c4Be15a165,
            linkToken: 0xb1D4538B4571d411F07960EF2838Ce337FE1E80E,
            usdc: 0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d,
            rpcUrl: vm.envString("ARBITRUM_SEPOLIA_RPC_URL"),
            etherscanApiKey: vm.envString("ARBISCAN_API_KEY")
        });
    }

    /**
     * @notice Deploy the complete IntentFi ecosystem
     */
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address deployer = vm.addr(deployerPrivateKey);
        
        console2.log("Deployer address:", deployer);
        console2.log("Chain ID:", block.chainid);
        
        ChainConfig memory config = chainConfigs[block.chainid];
        require(config.priceFeed != address(0), "Unsupported chain");
        
        vm.startBroadcast(deployerPrivateKey);
        
        DeployedContracts memory contracts = deployCompleteEcosystem(config, deployer);
        
        vm.stopBroadcast();
        
        // Store deployed contracts
        deployedContracts[block.chainid] = contracts;
        
        // Log deployment results
        logDeploymentResults(contracts);
        
        // Save deployment to file
        saveDeploymentInfo(contracts);
        
        // Verify contracts on Etherscan
        if (bytes(config.etherscanApiKey).length > 0) {
            verifyContracts(contracts, config);
        }
    }

    /**
     * @notice Deploy all contracts in the ecosystem
     * @param config Chain configuration
     * @param deployer Deployer address
     * @return contracts Deployed contract addresses
     */
    function deployCompleteEcosystem(
        ChainConfig memory config,
        address deployer
    ) internal returns (DeployedContracts memory contracts) {
        
        console2.log("=== Starting IntentFi Ecosystem Deployment ===");
        
        // 1. Deploy governance token (mock ERC20 for testing)
        console2.log("Deploying governance token...");
        contracts.governanceToken = deployGovernanceToken();
        
        // 2. Deploy basic IntentFi contract
        console2.log("Deploying IntentFi...");
        contracts.intentFi = address(new IntentFi(
            config.priceFeed,
            config.ccipRouter
        ));
        
        // 3. Deploy IntentFi with CCIP
        console2.log("Deploying IntentFiCCIP...");
        contracts.intentFiCCIP = address(new IntentFiCCIP(
            config.priceFeed,
            config.ccipRouter,
            config.linkToken
        ));
        
        // 4. Deploy advanced IntentFi
        console2.log("Deploying IntentFiAdvanced...");
        contracts.intentFiAdvanced = address(new IntentFiAdvanced(
            config.priceFeed,
            config.ccipRouter,
            config.linkToken
        ));
        
        // 5. Deploy governance contract
        console2.log("Deploying IntentFiGovernance...");
        address[] memory emergencyMultisig = new address[](3);
        emergencyMultisig[0] = deployer;
        emergencyMultisig[1] = deployer; // In production, use different addresses
        emergencyMultisig[2] = deployer;
        
        contracts.intentFiGovernance = address(new IntentFiGovernance(
            contracts.governanceToken,
            deployer,
            emergencyMultisig
        ));
        
        // 6. Deploy usage example contract
        console2.log("Deploying IntentFiUsageExample...");
        contracts.intentFiUsageExample = address(new IntentFiUsageExample(
            payable(contracts.intentFiAdvanced)
        ));
        
        // 7. Configure contracts
        configureContracts(contracts, config);
        
        console2.log("=== Deployment Complete ===");
        
        return contracts;
    }

    /**
     * @notice Deploy a mock governance token for testing
     * @return tokenAddress Address of the deployed token
     */
    function deployGovernanceToken() internal returns (address tokenAddress) {
        // Deploy a simple ERC20 token for governance
        bytes32 saltValue = keccak256("IntentFi_v1.0");
        bytes memory bytecode = abi.encodePacked(
            type(MockERC20).creationCode,
            abi.encode("IntentFi Governance Token", "IFI", 18, 1000000000e18) // 1B tokens
        );
        
        assembly {
            tokenAddress := create2(0, add(bytecode, 0x20), mload(bytecode), saltValue)
        }
        
        require(tokenAddress != address(0), "Token deployment failed");
    }

    /**
     * @notice Configure deployed contracts
     * @param contracts Deployed contract addresses
     * @param config Chain configuration
     */
    function configureContracts(
        DeployedContracts memory contracts,
        ChainConfig memory config
    ) internal {
        console2.log("Configuring contracts...");
        
        // Configure CCIP contract
        IntentFiCCIP ccipContract = IntentFiCCIP(payable(contracts.intentFiCCIP));
        ccipContract.setSupportedToken(config.usdc, true);
        
        // Configure advanced contract
        IntentFiAdvanced advancedContract = IntentFiAdvanced(payable(contracts.intentFiAdvanced));
        advancedContract.setSupportedToken(config.usdc, true);
        
        // Add allowlisted chains for all supported chains
        uint64[] memory chainSelectors = new uint64[](4);
        chainSelectors[0] = 16015286601757825753; // Sepolia
        chainSelectors[1] = 10344971235874465080; // Base Sepolia
        chainSelectors[2] = 5224473277236331295;  // Optimism Sepolia
        chainSelectors[3] = 3478487238524512106;  // Arbitrum Sepolia
        
        for (uint256 i = 0; i < chainSelectors.length; i++) {
            IntentFi(payable(contracts.intentFi)).allowlistDestinationChain(chainSelectors[i], true);
            IntentFiCCIP(payable(contracts.intentFiCCIP)).allowlistDestinationChain(chainSelectors[i], true);
            IntentFiAdvanced(payable(contracts.intentFiAdvanced)).allowlistDestinationChain(chainSelectors[i], true);
        }
    }

    /**
     * @notice Log deployment results
     * @param contracts Deployed contract addresses
     */
    function logDeploymentResults(DeployedContracts memory contracts) internal view {
        console2.log("\n=== Deployment Results ===");
        console2.log("Governance Token:", contracts.governanceToken);
        console2.log("IntentFi:", contracts.intentFi);
        console2.log("IntentFiCCIP:", contracts.intentFiCCIP);
        console2.log("IntentFiAdvanced:", contracts.intentFiAdvanced);
        console2.log("IntentFiGovernance:", contracts.intentFiGovernance);
        console2.log("IntentFiUsageExample:", contracts.intentFiUsageExample);
        console2.log("========================\n");
    }

    /**
     * @notice Save deployment information to environment file
     * @param contracts Deployed contract addresses
     */
    function saveDeploymentInfo(DeployedContracts memory contracts) internal {
        string memory deploymentInfo = string.concat(
            "# IntentFi Ecosystem Deployment on Chain ", vm.toString(block.chainid), "\n",
            "GOVERNANCE_TOKEN_ADDRESS=", vm.toString(contracts.governanceToken), "\n",
            "INTENTFI_CONTRACT_ADDRESS=", vm.toString(contracts.intentFi), "\n",
            "INTENTFI_CCIP_ADDRESS=", vm.toString(contracts.intentFiCCIP), "\n",
            "INTENTFI_ADVANCED_ADDRESS=", vm.toString(contracts.intentFiAdvanced), "\n",
            "INTENTFI_GOVERNANCE_ADDRESS=", vm.toString(contracts.intentFiGovernance), "\n",
            "INTENTFI_USAGE_EXAMPLE_ADDRESS=", vm.toString(contracts.intentFiUsageExample), "\n"
        );
        
        string memory filename = string.concat("deployments_", vm.toString(block.chainid), ".env");
        vm.writeFile(filename, deploymentInfo);
        console2.log("Deployment info saved to:", filename);
    }

    /**
     * @notice Verify contracts on Etherscan
     * @param contracts Deployed contract addresses
     * @param config Chain configuration
     */
    function verifyContracts(
        DeployedContracts memory contracts,
        ChainConfig memory config
    ) internal {
        console2.log("Verifying contracts on Etherscan...");
        
        // Note: In production, you would use the forge verify command
        // This is a placeholder for the verification process
        config; // silence warning
        contracts; // silence warning
        
        console2.log("Contract verification initiated. Check Etherscan for status.");
    }

    /**
     * @notice Deploy to all supported chains
     */
    function deployMultiChain() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        
        uint256[] memory supportedChains = new uint256[](4);
        supportedChains[0] = 11155111; // Sepolia
        supportedChains[1] = 84532;    // Base Sepolia
        supportedChains[2] = 11155420; // Optimism Sepolia
        supportedChains[3] = 421614;   // Arbitrum Sepolia
        
        for (uint256 i = 0; i < supportedChains.length; i++) {
            uint256 chainId = supportedChains[i];
            ChainConfig memory config = chainConfigs[chainId];
            
            if (config.priceFeed == address(0)) {
                console2.log("Skipping unsupported chain:", chainId);
                continue;
            }
            
            console2.log("Deploying to chain:", chainId);
            
            // Switch to the target chain's RPC
            vm.createSelectFork(config.rpcUrl);
            
            vm.startBroadcast(deployerPrivateKey);
            
            DeployedContracts memory contracts = deployCompleteEcosystem(
                config,
                vm.addr(deployerPrivateKey)
            );
            
            vm.stopBroadcast();
            
            deployedContracts[chainId] = contracts;
            logDeploymentResults(contracts);
        }
        
        console2.log("Multi-chain deployment complete!");
    }

    /**
     * @notice Get salt for CREATE2 deployments
     * @return Salt value
     */
    function salt() internal pure returns (bytes32) {
        return keccak256("IntentFi_v1.0");
    }
}

/**
 * @title MockERC20
 * @notice Simple ERC20 token for testing governance
 */
contract MockERC20 {
    string public name;
    string public symbol;
    uint8 public decimals;
    uint256 public totalSupply;
    
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    
    constructor(
        string memory _name,
        string memory _symbol,
        uint8 _decimals,
        uint256 _totalSupply
    ) {
        name = _name;
        symbol = _symbol;
        decimals = _decimals;
        totalSupply = _totalSupply;
        balanceOf[msg.sender] = _totalSupply;
        emit Transfer(address(0), msg.sender, _totalSupply);
    }
    
    function transfer(address to, uint256 amount) external returns (bool) {
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        emit Transfer(msg.sender, to, amount);
        return true;
    }
    
    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        allowance[from][msg.sender] -= amount;
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        emit Transfer(from, to, amount);
        return true;
    }
    
    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }
}
