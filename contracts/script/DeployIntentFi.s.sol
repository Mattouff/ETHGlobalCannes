// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Script, console2} from "forge-std/Script.sol";
import {IntentFi} from "../src/IntentFi.sol";

/**
 * @title DeployIntentFi
 * @notice Deployment script for IntentFi contract
 */
contract DeployIntentFi is Script {
    // Network configurations
    struct NetworkConfig {
        address ethUsdPriceFeed;
        address ccipRouter;
        uint64 chainSelector;
    }

    // Sepolia Testnet addresses
    NetworkConfig public sepoliaConfig = NetworkConfig({
        ethUsdPriceFeed: 0x694AA1769357215DE4FAC081bf1f309aDC325306,
        ccipRouter: 0x0BF3dE8c5D3e8A2B34D2BEeB17ABfCeBaf363A59,
        chainSelector: 16015286601757825753
    });

    // Base Sepolia Testnet addresses  
    NetworkConfig public baseSepoliaConfig = NetworkConfig({
        ethUsdPriceFeed: 0x4aDC67696bA383F43DD60A9e78F2C97Fbbfc7cb1,
        ccipRouter: 0xd3b06CEBF099Ce7Da4acCf578AAEfd5f4e89C8bA,
        chainSelector: 10344971235874465080
    });

    // Optimism Sepolia Testnet addresses
    NetworkConfig public optimismSepoliaConfig = NetworkConfig({
        ethUsdPriceFeed: 0x61Ec26aA57019C486B10502285c5A3D4A4750AD7,
        ccipRouter: 0x114A20A10b43D4115e5aeef7345a1A71d2a60C57,
        chainSelector: 5224473277236331295
    });

    // Arbitrum Sepolia Testnet addresses
    NetworkConfig public arbitrumSepoliaConfig = NetworkConfig({
        ethUsdPriceFeed: 0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165,
        ccipRouter: 0x2a9C5afB0d0e4BAb2BCdaE109EC4b0c4Be15a165,
        chainSelector: 3478487238524512106
    });

    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        
        vm.startBroadcast(deployerPrivateKey);

        NetworkConfig memory config = getNetworkConfig();
        
        console2.log("Deploying IntentFi on chain:", block.chainid);
        console2.log("Using ETH/USD Price Feed:", config.ethUsdPriceFeed);
        console2.log("Using CCIP Router:", config.ccipRouter);

        IntentFi intentFi = new IntentFi(
            config.ethUsdPriceFeed,
            config.ccipRouter
        );

        console2.log("IntentFi deployed at:", address(intentFi));

        // Setup initial allowlisted chains
        setupInitialConfiguration(intentFi, config);

        vm.stopBroadcast();
    }

    function getNetworkConfig() internal view returns (NetworkConfig memory) {
        uint256 chainId = block.chainid;
        
        if (chainId == 11155111) { // Sepolia
            return sepoliaConfig;
        } else if (chainId == 84532) { // Base Sepolia
            return baseSepoliaConfig;
        } else if (chainId == 11155420) { // Optimism Sepolia
            return optimismSepoliaConfig;
        } else if (chainId == 421614) { // Arbitrum Sepolia
            return arbitrumSepoliaConfig;
        } else {
            revert("Unsupported network");
        }
    }

    function setupInitialConfiguration(IntentFi intentFi, NetworkConfig memory config) internal {
        console2.log("Setting up initial configuration...");

        // Allowlist destination chains
        intentFi.allowlistDestinationChain(sepoliaConfig.chainSelector, true);
        intentFi.allowlistDestinationChain(baseSepoliaConfig.chainSelector, true);
        intentFi.allowlistDestinationChain(optimismSepoliaConfig.chainSelector, true);
        intentFi.allowlistDestinationChain(arbitrumSepoliaConfig.chainSelector, true);

        console2.log("Initial configuration completed");
    }
}
