import { ThemedText } from "@/components/ThemedText";
import { ThemedView } from "@/components/ThemedView";
import { AppColors, CommonStyles } from "@/constants/AppStyles";
import { useApp } from "@/contexts/AppContext";
import { useState } from "react";
import {
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

export default function TransactionsScreen() {
  const { state } = useApp();
  const [filter, setFilter] = useState<"all" | "swap" | "bridge" | "stake">(
    "all"
  );

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "swap":
        return "🔄";
      case "bridge":
        return "🌉";
      case "stake":
        return "💎";
      default:
        return "⚡";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending":
        return "#F59E0B";
      case "confirmed":
        return "#10B981";
      case "failed":
        return "#EF4444";
      default:
        return "#6B7280";
    }
  };

  const getChainIcon = (chain: string) => {
    switch (chain.toLowerCase()) {
      case "ethereum":
        return "🔷";
      case "polygon":
        return "🟣";
      case "arbitrum":
        return "🔵";
      case "optimism":
        return "🔴";
      default:
        return "⚡";
    }
  };

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    if (diff < 60000) return "Just now";
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;

    return date.toLocaleDateString();
  };

  const truncateHash = (hash: string) => {
    return `${hash.slice(0, 6)}...${hash.slice(-4)}`;
  };

  const filteredTransactions =
    filter === "all"
      ? state.transactions
      : state.transactions.filter((tx) => tx.type === filter);

  return (
    <ThemedView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <ThemedText type="title">Transaction History</ThemedText>
          <ThemedText style={styles.subtitle}>
            Cross-chain transaction tracking
          </ThemedText>
        </View>

        {/* Filter Tabs */}
        <View style={styles.section}>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            style={styles.filterContainer}
          >
            {(["all", "swap", "bridge", "stake"] as const).map((filterType) => (
              <TouchableOpacity
                key={filterType}
                style={[
                  styles.filterTab,
                  filter === filterType && styles.activeFilterTab,
                ]}
                onPress={() => setFilter(filterType)}
              >
                <Text
                  style={[
                    styles.filterText,
                    filter === filterType && styles.activeFilterText,
                  ]}
                >
                  {filterType.charAt(0).toUpperCase() + filterType.slice(1)}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {/* Transaction Stats */}
        <View style={styles.section}>
          <View style={styles.statsCard}>
            <View style={styles.statItem}>
              <ThemedText style={styles.statValue}>
                {state.transactions.length}
              </ThemedText>
              <ThemedText style={styles.statLabel}>
                Total Transactions
              </ThemedText>
            </View>
            <View style={styles.statItem}>
              <ThemedText style={styles.statValue}>
                {
                  state.transactions.filter((tx) => tx.status === "confirmed")
                    .length
                }
              </ThemedText>
              <ThemedText style={styles.statLabel}>Confirmed</ThemedText>
            </View>
            <View style={styles.statItem}>
              <ThemedText style={styles.statValue}>
                {
                  state.transactions.filter((tx) => tx.status === "pending")
                    .length
                }
              </ThemedText>
              <ThemedText style={styles.statLabel}>Pending</ThemedText>
            </View>
            <View style={styles.statItem}>
              <ThemedText style={styles.statValue}>4</ThemedText>
              <ThemedText style={styles.statLabel}>Chains</ThemedText>
            </View>
          </View>
        </View>

        {/* Transactions List */}
        <View style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>
            Recent Transactions
          </ThemedText>

          {filteredTransactions.length > 0 ? (
            filteredTransactions.map((transaction) => (
              <View key={transaction.id} style={styles.transactionCard}>
                <View style={styles.transactionHeader}>
                  <View style={styles.transactionMeta}>
                    <Text style={styles.typeIcon}>
                      {getTypeIcon(transaction.type)}
                    </Text>
                    <View>
                      <View style={styles.transactionType}>
                        <ThemedText style={styles.typeText}>
                          {transaction.type.toUpperCase()}
                        </ThemedText>
                        <View
                          style={[
                            styles.statusBadge,
                            {
                              backgroundColor: getStatusColor(
                                transaction.status
                              ),
                            },
                          ]}
                        >
                          <Text style={styles.statusText}>
                            {transaction.status.toUpperCase()}
                          </Text>
                        </View>
                      </View>
                      <ThemedText style={styles.transactionTime}>
                        {formatTime(transaction.timestamp)}
                      </ThemedText>
                    </View>
                  </View>
                  <TouchableOpacity style={styles.viewButton}>
                    <ThemedText style={styles.viewButtonText}>View</ThemedText>
                  </TouchableOpacity>
                </View>

                <View style={styles.transactionDetails}>
                  <View style={styles.tradeFlow}>
                    <View style={styles.tokenInfo}>
                      <Text style={styles.chainIcon}>
                        {getChainIcon(transaction.fromChain)}
                      </Text>
                      <View>
                        <ThemedText style={styles.tokenAmount}>
                          {transaction.amount} {transaction.fromToken}
                        </ThemedText>
                        <ThemedText style={styles.chainName}>
                          {transaction.fromChain}
                        </ThemedText>
                      </View>
                    </View>

                    <Text style={styles.arrowIcon}>→</Text>

                    <View style={styles.tokenInfo}>
                      <Text style={styles.chainIcon}>
                        {getChainIcon(transaction.toChain)}
                      </Text>
                      <View>
                        <ThemedText style={styles.tokenAmount}>
                          {transaction.toToken}
                        </ThemedText>
                        <ThemedText style={styles.chainName}>
                          {transaction.toChain}
                        </ThemedText>
                      </View>
                    </View>
                  </View>

                  <View style={styles.transactionInfo}>
                    <View style={styles.infoRow}>
                      <ThemedText style={styles.infoLabel}>Hash:</ThemedText>
                      <TouchableOpacity>
                        <ThemedText style={styles.hashText}>
                          {truncateHash(transaction.hash)}
                        </ThemedText>
                      </TouchableOpacity>
                    </View>

                    {transaction.gasUsed && (
                      <View style={styles.infoRow}>
                        <ThemedText style={styles.infoLabel}>
                          Gas Used:
                        </ThemedText>
                        <ThemedText style={styles.infoValue}>
                          {transaction.gasUsed} ETH
                        </ThemedText>
                      </View>
                    )}
                  </View>
                </View>
              </View>
            ))
          ) : (
            <View style={styles.emptyState}>
              <Text style={styles.emptyIcon}>📜</Text>
              <ThemedText type="subtitle" style={styles.emptyTitle}>
                No {filter === "all" ? "" : filter} transactions
              </ThemedText>
              <ThemedText style={styles.emptySubtitle}>
                Your transaction history will appear here once you start
                trading.
              </ThemedText>
            </View>
          )}
        </View>

        {/* Transaction Insights */}
        <View style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>
            Transaction Insights
          </ThemedText>

          <View style={styles.insightCard}>
            <View style={styles.insightRow}>
              <ThemedText style={styles.insightLabel}>
                Average Gas Cost:
              </ThemedText>
              <ThemedText style={styles.insightValue}>0.0045 ETH</ThemedText>
            </View>

            <View style={styles.insightRow}>
              <ThemedText style={styles.insightLabel}>
                Total Gas Spent:
              </ThemedText>
              <ThemedText style={styles.insightValue}>
                0.0045 ETH ($18.20)
              </ThemedText>
            </View>

            <View style={styles.insightRow}>
              <ThemedText style={styles.insightLabel}>Success Rate:</ThemedText>
              <ThemedText style={[styles.insightValue, styles.successRate]}>
                100%
              </ThemedText>
            </View>

            <View style={styles.insightRow}>
              <ThemedText style={styles.insightLabel}>
                Most Used Chain:
              </ThemedText>
              <ThemedText style={styles.insightValue}>Ethereum</ThemedText>
            </View>
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>
            Quick Actions
          </ThemedText>

          <View style={styles.quickActions}>
            <TouchableOpacity style={styles.actionButton}>
              <Text style={styles.actionIcon}>📊</Text>
              <ThemedText style={styles.actionText}>Export CSV</ThemedText>
            </TouchableOpacity>
            <TouchableOpacity style={styles.actionButton}>
              <Text style={styles.actionIcon}>🔍</Text>
              <ThemedText style={styles.actionText}>Advanced Filter</ThemedText>
            </TouchableOpacity>
            <TouchableOpacity style={styles.actionButton}>
              <Text style={styles.actionIcon}>🔄</Text>
              <ThemedText style={styles.actionText}>Refresh</ThemedText>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: AppColors.screenBackground,
  },
  scrollView: {
    flex: 1,
  },
  header: {
    ...CommonStyles.header,
  },
  subtitle: {
    ...CommonStyles.headerSubtitle,
  },
  section: {
    ...CommonStyles.section,
  },
  sectionTitle: {
    ...CommonStyles.sectionTitle,
  },
  filterContainer: {
    marginBottom: 16,
  },
  filterTab: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
    borderRadius: 20,
    marginRight: 12,
  },
  activeFilterTab: {
    backgroundColor: AppColors.primary,
    borderColor: AppColors.primary,
  },
  filterText: {
    fontSize: 14,
    fontWeight: "500",
    color: AppColors.textSecondary,
  },
  activeFilterText: {
    color: AppColors.textInverse,
  },
  statsCard: {
    ...CommonStyles.card,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
    flexDirection: "row",
    justifyContent: "space-around",
  },
  statItem: {
    alignItems: "center",
  },
  statValue: {
    color: AppColors.textPrimary,
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 4,
  },
  statLabel: {
    color: AppColors.textMuted,
    fontSize: 12,
    textAlign: "center",
  },
  transactionCard: {
    ...CommonStyles.card,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
  },
  transactionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  transactionMeta: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    flex: 1,
  },
  typeIcon: {
    fontSize: 24,
  },
  transactionType: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  typeText: {
    color: AppColors.textPrimary,
    fontSize: 14,
    fontWeight: "600",
  },
  statusBadge: {
    ...CommonStyles.statusBadge,
  },
  statusText: {
    ...CommonStyles.statusBadgeText,
  },
  transactionTime: {
    color: AppColors.textMuted,
    fontSize: 12,
    marginTop: 2,
  },
  viewButton: {
    backgroundColor: AppColors.primary,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  viewButtonText: {
    color: AppColors.textInverse,
    fontSize: 12,
    fontWeight: "600",
  },
  transactionDetails: {
    gap: 16,
  },
  tradeFlow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  tokenInfo: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    flex: 1,
  },
  chainIcon: {
    fontSize: 20,
  },
  tokenAmount: {
    color: AppColors.textPrimary,
    fontSize: 14,
    fontWeight: "600",
  },
  chainName: {
    color: AppColors.textMuted,
    fontSize: 12,
    marginTop: 2,
  },
  arrowIcon: {
    fontSize: 16,
    color: AppColors.textMuted,
    marginHorizontal: 16,
  },
  transactionInfo: {
    gap: 8,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: AppColors.divider,
  },
  infoRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  infoLabel: {
    color: AppColors.textSecondary,
    fontSize: 12,
  },
  infoValue: {
    color: AppColors.textPrimary,
    fontSize: 12,
    fontWeight: "500",
  },
  hashText: {
    fontSize: 12,
    fontWeight: "500",
    color: AppColors.primary,
  },
  emptyState: {
    alignItems: "center",
    padding: 40,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyTitle: {
    color: AppColors.textPrimary,
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 8,
    textAlign: "center",
  },
  emptySubtitle: {
    color: AppColors.textSecondary,
    fontSize: 14,
    textAlign: "center",
    lineHeight: 20,
  },
  insightCard: {
    ...CommonStyles.card,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
  },
  insightRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  insightLabel: {
    color: AppColors.textSecondary,
    fontSize: 14,
  },
  insightValue: {
    color: AppColors.textPrimary,
    fontSize: 14,
    fontWeight: "600",
  },
  successRate: {
    color: AppColors.success,
  },
  quickActions: {
    flexDirection: "row",
    justifyContent: "space-around",
  },
  actionButton: {
    alignItems: "center",
    padding: 16,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
    borderRadius: 12,
    minWidth: 80,
  },
  actionIcon: {
    fontSize: 20,
    marginBottom: 8,
  },
  actionText: {
    color: AppColors.textPrimary,
    fontSize: 12,
    textAlign: "center",
  },
});
