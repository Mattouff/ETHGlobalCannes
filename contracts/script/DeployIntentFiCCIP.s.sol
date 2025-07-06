// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Script, console2} from "forge-std/Script.sol";
import {IntentFiCCIP} from "../src/IntentFiCCIP.sol";

/**
 * @title DeployIntentFiCCIP
 * @notice Deployment script for IntentFiCCIP contract with cross-chain capabilities
 */
contract DeployIntentFiCCIP is Script {
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

    function run() external {
        // Load private key from environment, handling with or without 0x prefix
        string memory privateKeyStr = vm.envString("PRIVATE_KEY");
        uint256 deployerPrivateKey;

        // Check if the private key starts with 0x
        if (bytes(privateKeyStr).length >= 2 && bytes(privateKeyStr)[0] == 0x30 && bytes(privateKeyStr)[1] == 0x78) {
            // Has 0x prefix, parse directly
            deployerPrivateKey = vm.parseUint(privateKeyStr);
        } else {
            // No 0x prefix, add it
            deployerPrivateKey = vm.parseUint(string.concat("0x", privateKeyStr));
        }

        uint256 chainId = block.chainid;

        ChainConfig memory config = chainConfigs[chainId];
        require(config.priceFeed != address(0), "Chain not supported");

        vm.startBroadcast(deployerPrivateKey);

        console2.log("=== Deploying IntentFiCCIP ===");
        console2.log("Chain ID:", chainId);
        console2.log("Chain Selector:", config.chainSelector);
        console2.log("Price Feed:", config.priceFeed);
        console2.log("CCIP Router:", config.ccipRouter);
        console2.log("LINK Token:", config.linkToken);

        // Deploy IntentFiCCIP
        IntentFiCCIP intentFiCCIP = new IntentFiCCIP(config.priceFeed, config.ccipRouter, config.linkToken);

        console2.log("IntentFiCCIP deployed at:", address(intentFiCCIP));

        // Configure supported destination chains
        _configureCrossChainSupport(intentFiCCIP);

        vm.stopBroadcast();

        console2.log("=== Deployment Complete ===");
        console2.log("Contract Address:", address(intentFiCCIP));
        console2.log("Verification command:");
        console2.log(
            string.concat(
                "forge verify-contract ",
                vm.toString(address(intentFiCCIP)),
                " src/IntentFiCCIP.sol:IntentFiCCIP --chain-id ",
                vm.toString(chainId),
                " --constructor-args ",
                vm.toString(abi.encode(config.priceFeed, config.ccipRouter, config.linkToken))
            )
        );
    }

    function _configureCrossChainSupport(IntentFiCCIP intentFiCCIP) internal {
        console2.log("Configuring cross-chain support...");

        // Get all supported chain selectors
        uint64[] memory supportedChains = new uint64[](4);
        supportedChains[0] = 16015286601757825753; // Sepolia
        supportedChains[1] = 10344971235874465080; // Base Sepolia
        supportedChains[2] = 3478487238524512106; // Arbitrum Sepolia
        supportedChains[3] = 5224473277236331295; // Optimism Sepolia

        // Allowlist all destination chains
        for (uint256 i = 0; i < supportedChains.length; i++) {
            intentFiCCIP.allowlistDestinationChain(supportedChains[i], true);
            console2.log("Allowlisted chain selector:", supportedChains[i]);
        }

        console2.log("Cross-chain configuration complete");
    }

    /**
     * @notice Deploy to multiple chains (for testing)
     */
    function deployMultiChain() external {
        console2.log("=== Multi-Chain Deployment ===");

        // This would be called separately for each chain
        // Example: forge script script/DeployIntentFiCCIP.s.sol:DeployIntentFiCCIP --sig "deployMultiChain()" --rpc-url $SEPOLIA_RPC_URL

        this.run();
    }
}
