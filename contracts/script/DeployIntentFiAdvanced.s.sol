// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Script, console2} from "forge-std/Script.sol";
import {IntentFiAdvanced} from "../src/IntentFiAdvanced.sol";

/**
 * @title DeployIntentFiAdvanced
 * @notice Deployment script for IntentFiAdvanced contract with sophisticated DeFi strategies
 */
contract DeployIntentFiAdvanced is Script {
    // Chain configurations
    struct ChainConfig {
        uint64 chainSelector;
        address priceFeed;
        address ccipRouter;
        address linkToken;
    }

    mapping(uint256 => ChainConfig) public chainConfigs;

    function setUp() public {
        // Sepolia configuration
        chainConfigs[11155111] = ChainConfig({
            chainSelector: 16015286601757825753,
            priceFeed: 0x694AA1769357215DE4FAC081bf1f309aDC325306, // ETH/USD
            ccipRouter: 0x0BF3dE8c5D3e8A2B34D2BEeB17ABfCeBaf363A59,
            linkToken: 0x779877A7B0D9E8603169DdbD7836e478b4624789
        });

        // Base Sepolia configuration
        chainConfigs[84532] = ChainConfig({
            chainSelector: 10344971235874465080,
            priceFeed: 0x4aDC67696bA383F43DD60A9e78F2C97Fbbfc7cb1, // ETH/USD
            ccipRouter: 0xD3b06cEbF099CE7DA4AcCf578aaebFDBd6e88a93,
            linkToken: 0xE4aB69C077896252FAFBD49EFD26B5D171A32410
        });

        // Arbitrum Sepolia configuration
        chainConfigs[421614] = ChainConfig({
            chainSelector: 3478487238524512106,
            priceFeed: 0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165, // ETH/USD
            ccipRouter: 0x2a9C5afB0d0e4BAb2BCdaE109EC4b0c4Be15a165,
            linkToken: 0xb1D4538B4571d411F07960EF2838Ce337FE1E80E
        });

        // Optimism Sepolia configuration
        chainConfigs[11155420] = ChainConfig({
            chainSelector: 5224473277236331295,
            priceFeed: 0x61Ec26aA57019C486B10502285c5A3D4A4750AD7, // ETH/USD
            ccipRouter: 0x114A20A10b43D4115e5aeef7345a1A71d2a60C57,
            linkToken: 0xE4aB69C077896252FAFBD49EFD26B5D171A32410
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
        require(config.priceFeed != address(0), "Chain not supported");

        vm.startBroadcast(deployerPrivateKey);

        console2.log("=== Deploying IntentFiAdvanced ===");
        console2.log("Chain ID:", chainId);
        console2.log("Chain Selector:", config.chainSelector);
        console2.log("Price Feed:", config.priceFeed);
        console2.log("CCIP Router:", config.ccipRouter);
        console2.log("LINK Token:", config.linkToken);

        // Deploy IntentFiAdvanced
        IntentFiAdvanced intentFiAdvanced = new IntentFiAdvanced(config.priceFeed, config.ccipRouter, config.linkToken);

        console2.log("IntentFiAdvanced deployed at:", address(intentFiAdvanced));

        // Configure advanced strategy support
        _configureAdvancedStrategies(intentFiAdvanced);

        vm.stopBroadcast();

        console2.log("=== Deployment Complete ===");
        console2.log("Contract Address:", address(intentFiAdvanced));
        console2.log("Verification command:");
        console2.log(
            string.concat(
                "forge verify-contract ",
                vm.toString(address(intentFiAdvanced)),
                " src/IntentFiAdvanced.sol:IntentFiAdvanced --chain-id ",
                vm.toString(chainId),
                " --constructor-args ",
                vm.toString(abi.encode(config.priceFeed, config.ccipRouter, config.linkToken))
            )
        );
    }

    function _configureAdvancedStrategies(IntentFiAdvanced intentFiAdvanced) internal {
        console2.log("Configuring advanced strategies...");

        // Get all supported chain selectors
        uint64[] memory supportedChains = new uint64[](4);
        supportedChains[0] = 16015286601757825753; // Sepolia
        supportedChains[1] = 10344971235874465080; // Base Sepolia
        supportedChains[2] = 3478487238524512106; // Arbitrum Sepolia
        supportedChains[3] = 5224473277236331295; // Optimism Sepolia

        // Allowlist all destination chains
        for (uint256 i = 0; i < supportedChains.length; i++) {
            intentFiAdvanced.allowlistDestinationChain(supportedChains[i], true);
            console2.log("Allowlisted chain selector:", supportedChains[i]);
        }

        // Configure initial strategy parameters
        // Note: In production, these would be set via governance
        console2.log("Strategy configuration complete");
    }

    /**
     * @notice Deploy to multiple chains (for testing)
     */
    function deployMultiChain() external {
        console2.log("=== Multi-Chain Advanced Deployment ===");

        // This would be called separately for each chain
        // Example: forge script script/DeployIntentFiAdvanced.s.sol:DeployIntentFiAdvanced --sig "deployMultiChain()" --rpc-url $SEPOLIA_RPC_URL

        this.run();
    }

    /**
     * @notice Setup for testing environment
     */
    function deployForTesting() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");

        vm.startBroadcast(deployerPrivateKey);

        console2.log("=== Deploying IntentFiAdvanced for Testing ===");

        // Use mock addresses for testing
        address mockPriceFeed = address(0x1111111111111111111111111111111111111111);
        address mockCCIPRouter = address(0x2222222222222222222222222222222222222222);
        address mockLinkToken = address(0x3333333333333333333333333333333333333333);

        IntentFiAdvanced intentFiAdvanced = new IntentFiAdvanced(mockPriceFeed, mockCCIPRouter, mockLinkToken);

        console2.log("Test IntentFiAdvanced deployed at:", address(intentFiAdvanced));

        vm.stopBroadcast();
    }
}
