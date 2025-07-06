// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// Minimal interface definitions for CCIP mocking (no external dependencies)
library Client {
    struct EVMTokenAmount {
        address token;
        uint256 amount;
    }

    struct EVM2AnyMessage {
        bytes receiver;
        bytes data;
        EVMTokenAmount[] tokenAmounts;
        address feeToken;
        bytes extraArgs;
    }
}

interface IRouterClient {
    function isChainSupported(uint64 chainSelector) external view returns (bool);
    
    function getSupportedTokens(uint64 chainSelector) external view returns (address[] memory);
    
    function getFee(uint64 destinationChainSelector, Client.EVM2AnyMessage memory message)
        external
        view
        returns (uint256 fee);
    
    function ccipSend(uint64 destinationChainSelector, Client.EVM2AnyMessage calldata message)
        external
        payable
        returns (bytes32);
}

contract MockCCIPRouter is IRouterClient {
    uint256 private messageIdCounter = 1;
    
    mapping(uint64 => bool) public supportedChains;
    
    constructor() {
        // Add some supported chains for testing
        supportedChains[12345] = true;
        supportedChains[67890] = true;
    }

    function isChainSupported(uint64 chainSelector) external view returns (bool) {
        return supportedChains[chainSelector];
    }

    function getSupportedTokens(uint64 chainSelector) external pure returns (address[] memory) {
        chainSelector; // silence warning
        address[] memory tokens = new address[](0);
        return tokens;
    }

    function getFee(uint64 destinationChainSelector, Client.EVM2AnyMessage memory message)
        external
        pure
        returns (uint256 fee)
    {
        destinationChainSelector; // silence warning
        message; // silence warning
        return 0.001 ether; // Mock fee
    }

    function ccipSend(uint64 destinationChainSelector, Client.EVM2AnyMessage calldata message)
        external
        payable
        returns (bytes32)
    {
        destinationChainSelector; // silence warning
        message; // silence warning
        
        bytes32 messageId = bytes32(messageIdCounter);
        messageIdCounter++;
        
        return messageId;
    }
}
