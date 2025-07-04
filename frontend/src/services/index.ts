import { SUPPORTED_CHAINS, TRANSACTION_TYPES } from "../constants/config";
import { Asset, Intent, Transaction } from "../types";
import { generateTxHash } from "../utils/helpers";

/**
 * Service for AI Agent related operations
 */
export class AIAgentService {
  /**
   * Generate a new intent based on market conditions (simulated)
   */
  static generateIntent(): Intent {
    const types = Object.values(TRANSACTION_TYPES);
    const chains = Object.values(SUPPORTED_CHAINS);

    return {
      id: `intent_${Date.now()}`,
      type: types[Math.floor(Math.random() * types.length)] as Intent["type"],
      fromToken: "ETH",
      toToken: "USDC",
      fromChain: chains[Math.floor(Math.random() * chains.length)],
      toChain: chains[Math.floor(Math.random() * chains.length)],
      amount: (Math.random() * 2).toFixed(3),
      estimatedGas: (Math.random() * 0.01).toFixed(4),
      confidence: 0.7 + Math.random() * 0.25,
      reasoning: this.generateReasoning(),
      timestamp: Date.now(),
      status: "pending",
    };
  }

  /**
   * Generate reasoning text for intents
   */
  private static generateReasoning(): string {
    const reasons = [
      "Market volatility indicators suggest optimal timing for this trade.",
      "Cross-chain arbitrage opportunity detected with 12% profit potential.",
      "Gas fees are currently 65% below average - good time to execute.",
      "DeFi yield farming opportunity identified on target chain.",
      "Portfolio rebalancing recommended based on risk analysis.",
    ];

    return reasons[Math.floor(Math.random() * reasons.length)];
  }
}

/**
 * Service for transaction operations
 */
export class TransactionService {
  /**
   * Create transaction from approved intent
   */
  static createTransactionFromIntent(intent: Intent): Transaction {
    return {
      id: `tx_${Date.now()}`,
      hash: generateTxHash(),
      type: intent.type,
      fromToken: intent.fromToken,
      toToken: intent.toToken,
      fromChain: intent.fromChain,
      toChain: intent.toChain,
      amount: intent.amount,
      status: "pending",
      timestamp: Date.now(),
    };
  }

  /**
   * Simulate transaction confirmation
   */
  static async confirmTransaction(transactionId: string): Promise<void> {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve();
      }, 3000);
    });
  }
}

/**
 * Service for portfolio operations
 */
export class PortfolioService {
  /**
   * Calculate total portfolio value
   */
  static calculateTotalValue(assets: Asset[]): string {
    const total = assets.reduce((sum, asset) => {
      const value = parseFloat(asset.value.replace("$", "").replace(",", ""));
      return sum + value;
    }, 0);

    return `$${total.toLocaleString()}`;
  }

  /**
   * Group assets by chain
   */
  static groupAssetsByChain(assets: Asset[]): Record<string, Asset[]> {
    return assets.reduce((acc, asset) => {
      if (!acc[asset.chain]) {
        acc[asset.chain] = [];
      }
      acc[asset.chain].push(asset);
      return acc;
    }, {} as Record<string, Asset[]>);
  }

  /**
   * Calculate chain allocation percentages
   */
  static calculateChainAllocations(assets: Asset[]): Record<string, number> {
    const chainValues = this.groupAssetsByChain(assets);
    const totalValue = parseFloat(
      this.calculateTotalValue(assets).replace("$", "").replace(",", "")
    );

    const allocations: Record<string, number> = {};

    Object.entries(chainValues).forEach(([chain, chainAssets]) => {
      const chainValue = chainAssets.reduce((sum, asset) => {
        return sum + parseFloat(asset.value.replace("$", "").replace(",", ""));
      }, 0);

      allocations[chain] = (chainValue / totalValue) * 100;
    });

    return allocations;
  }
}
