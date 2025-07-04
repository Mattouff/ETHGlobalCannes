import { useCallback } from "react";
import { Alert } from "react-native";
import { useApp } from "../../contexts/AppContext";
import { Asset } from "../types";

/**
 * Custom hook for intent management operations
 */
export const useIntentActions = () => {
  const { state, approveIntent, rejectIntent } = useApp();

  const handleApproveIntent = useCallback(
    (intentId: string) => {
      Alert.alert(
        "Approve Intent",
        "Are you sure you want to approve this trading intent?",
        [
          { text: "Cancel", style: "cancel" },
          {
            text: "Approve",
            style: "default",
            onPress: () => approveIntent(intentId),
          },
        ]
      );
    },
    [approveIntent]
  );

  const handleRejectIntent = useCallback(
    (intentId: string) => {
      Alert.alert(
        "Reject Intent",
        "Are you sure you want to reject this trading intent?",
        [
          { text: "Cancel", style: "cancel" },
          {
            text: "Reject",
            style: "destructive",
            onPress: () => rejectIntent(intentId),
          },
        ]
      );
    },
    [rejectIntent]
  );

  const getPendingIntents = useCallback(() => {
    return state.intents.filter((intent) => intent.status === "pending");
  }, [state.intents]);

  const getCompletedIntents = useCallback(() => {
    return state.intents.filter((intent) => intent.status !== "pending");
  }, [state.intents]);

  return {
    handleApproveIntent,
    handleRejectIntent,
    getPendingIntents,
    getCompletedIntents,
    intents: state.intents,
  };
};

/**
 * Custom hook for transaction operations
 */
export const useTransactionActions = () => {
  const { state } = useApp();

  const getFilteredTransactions = useCallback(
    (filter: "all" | "swap" | "bridge" | "stake") => {
      if (filter === "all") return state.transactions;
      return state.transactions.filter((tx) => tx.type === filter);
    },
    [state.transactions]
  );

  const getTransactionStats = useCallback(() => {
    const total = state.transactions.length;
    const confirmed = state.transactions.filter(
      (tx) => tx.status === "confirmed"
    ).length;
    const pending = state.transactions.filter(
      (tx) => tx.status === "pending"
    ).length;

    return { total, confirmed, pending };
  }, [state.transactions]);

  return {
    transactions: state.transactions,
    getFilteredTransactions,
    getTransactionStats,
  };
};

/**
 * Custom hook for portfolio calculations
 */
export const usePortfolioData = () => {
  const { state } = useApp();

  const getAssetsByChain = useCallback(() => {
    return state.assets.reduce((acc: Record<string, Asset[]>, asset: Asset) => {
      if (!acc[asset.chain]) {
        acc[asset.chain] = [];
      }
      acc[asset.chain].push(asset);
      return acc;
    }, {} as Record<string, Asset[]>);
  }, [state.assets]);

  const getChainValues = useCallback(() => {
    const assetsByChain = getAssetsByChain();

    return Object.entries(assetsByChain).map(([chain, assets]) => {
      const totalValue = assets.reduce((sum: number, asset: Asset) => {
        return sum + parseFloat(asset.value.replace("$", "").replace(",", ""));
      }, 0);
      return { chain, totalValue, assets };
    });
  }, [getAssetsByChain]);

  const getPortfolioStats = useCallback(() => {
    const totalAssets = state.assets.length;
    const totalChains = new Set(state.assets.map((asset) => asset.chain)).size;

    return { totalAssets, totalChains };
  }, [state.assets]);

  return {
    assets: state.assets,
    totalPortfolioValue: state.totalPortfolioValue,
    getAssetsByChain,
    getChainValues,
    getPortfolioStats,
  };
};
