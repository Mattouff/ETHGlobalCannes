// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Script, console2} from "forge-std/Script.sol";
import {IntentFi} from "../src/IntentFi.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title InteractIntentFi
 * @notice Script pour interagir avec le contrat IntentFi déployé
 */
contract InteractIntentFi is Script {
    IntentFi public intentFi;
    
    // Adresses de tokens sur les différents réseaux
    mapping(uint256 => address) public usdcAddresses;
    
    function setUp() public {
        // Configuration des adresses USDC par chaîne
        usdcAddresses[11155111] = 0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238; // Sepolia USDC
        usdcAddresses[84532] = 0x036CbD53842c5426634e7929541eC2318f3dCF7e;     // Base Sepolia USDC
        usdcAddresses[11155420] = 0x5fd84259d66Cd46123540766Be93DFE6D43130D7;   // Optimism Sepolia USDC
        usdcAddresses[421614] = 0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d;    // Arbitrum Sepolia USDC
    }

    function run() external {
        // Adresse du contrat IntentFi déployé (à mettre à jour après déploiement)
        address intentFiAddress = vm.envAddress("INTENTFI_CONTRACT_ADDRESS");
        intentFi = IntentFi(payable(intentFiAddress));
        
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        
        vm.startBroadcast(deployerPrivateKey);
        
        // Exemples d'interaction
        demonstrateCreateIntent();
        demonstrateCheckPrice();
        demonstrateGetUserIntents();
        
        vm.stopBroadcast();
    }

    /**
     * @notice Démontre la création d'un intent
     */
    function demonstrateCreateIntent() internal {
        console2.log("=== Creating Intent ===");
        
        uint256 chainId = block.chainid;
        address usdcAddress = usdcAddresses[chainId];
        
        if (usdcAddress == address(0)) {
            console2.log("USDC address not configured for this chain");
            return;
        }
        
        // Paramètres de l'intent
        uint256 triggerPrice = 3500 * 1e8; // $3500 avec 8 décimales
        uint256 amount = 50e6; // 50 USDC avec 6 décimales
        uint64 destinationChain = getDestinationChain(chainId);
        address receiver = msg.sender; // Envoyer à soi-même pour la démo
        
        console2.log("Trigger Price: $", triggerPrice / 1e8);
        console2.log("Amount: ", amount / 1e6, " USDC");
        console2.log("Destination Chain Selector: ", destinationChain);
        
        // Vérifier et approuver USDC si nécessaire
        IERC20 usdc = IERC20(usdcAddress);
        uint256 balance = usdc.balanceOf(msg.sender);
        
        if (balance >= amount) {
            console2.log("Approving USDC...");
            usdc.approve(address(intentFi), amount);
            
            console2.log("Creating intent...");
            uint256 intentId = intentFi.createIntent(
                IntentFi.IntentType.SEND_IF_PRICE_ABOVE,
                int256(triggerPrice),
                amount,
                usdcAddress,
                destinationChain,
                receiver
            );
            
            console2.log("Intent created with ID: ", intentId);
        } else {
            console2.log("Insufficient USDC balance. Have: ", balance / 1e6, " Need: ", amount / 1e6);
        }
    }

    /**
     * @notice Démontre la vérification du prix actuel
     */
    function demonstrateCheckPrice() internal {
        console2.log("\n=== Current Price ===");
        
        int256 currentPrice = intentFi.getCurrentPrice();
        console2.log("Current ETH/USD Price: $", uint256(currentPrice) / 1e8);
        
        // Vérifier s'il y a des intents prêts à être exécutés
        (bool upkeepNeeded, ) = intentFi.checkUpkeep("");
        
        if (upkeepNeeded) {
            console2.log("Ready: Some intents are ready for execution!");
        } else {
            console2.log("Waiting: No intents ready for execution");
        }
    }

    /**
     * @notice Démontre la récupération des intents utilisateur
     */
    function demonstrateGetUserIntents() internal {
        console2.log("\n=== User Intents ===");
        
        uint256[] memory userIntents = intentFi.getUserIntents(msg.sender);
        console2.log("Number of intents: ", userIntents.length);
        
        for (uint256 i = 0; i < userIntents.length; i++) {
            IntentFi.Intent memory intent = intentFi.getIntentDetails(userIntents[i]);
            
            console2.log("Intent ID: ", intent.id);
            console2.log("  Type: ", uint8(intent.intentType));
            console2.log("  Trigger Price: $", uint256(intent.triggerPrice) / 1e8);
            console2.log("  Amount: ", intent.amount);
            console2.log("  Status: ", uint8(intent.status));
            console2.log("  Destination Chain: ", intent.destinationChainSelector);
            console2.log("---");
        }
    }

    /**
     * @notice Obtenir la chaîne de destination basée sur la chaîne actuelle
     */
    function getDestinationChain(uint256 chainId) internal pure returns (uint64) {
        if (chainId == 11155111) { // Sepolia
            return 10344971235874465080; // Base Sepolia
        } else if (chainId == 84532) { // Base Sepolia
            return 5224473277236331295;  // Optimism Sepolia
        } else if (chainId == 11155420) { // Optimism Sepolia
            return 3478487238524512106;  // Arbitrum Sepolia
        } else if (chainId == 421614) { // Arbitrum Sepolia
            return 16015286601757825753; // Sepolia
        } else {
            revert("Unsupported chain");
        }
    }

    /**
     * @notice Fonction pour exécuter manuellement un intent (si autorisé)
     */
    function executeIntent(uint256 intentId) external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);
        
        console2.log("Executing intent with ID: ", intentId);
        intentFi.executeIntent(intentId);
        console2.log("Intent executed successfully!");
        
        vm.stopBroadcast();
    }

    /**
     * @notice Fonction pour annuler un intent
     */
    function cancelIntent(uint256 intentId) external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);
        
        console2.log("Cancelling intent with ID: ", intentId);
        intentFi.cancelIntent(intentId);
        console2.log("Intent cancelled successfully!");
        
        vm.stopBroadcast();
    }
}
