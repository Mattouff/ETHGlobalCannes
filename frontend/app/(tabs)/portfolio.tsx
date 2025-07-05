import { ThemedText } from "@/components/ThemedText";
import { ThemedView } from "@/components/ThemedView";
import { AppColors, CommonStyles } from "@/constants/AppStyles";
import { usePortfolioData } from "@/src/hooks";
import { Asset } from "@/src/types";
import { getChainIcon } from "@/src/utils/helpers";
import {
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

export default function PortfolioScreen() {
  const { totalPortfolioValue, getChainValues, getPortfolioStats } =
    usePortfolioData();

  const chainValues = getChainValues();
  const portfolioStats = getPortfolioStats();

  return (
    <ThemedView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <ThemedText type="title">Portfolio</ThemedText>
          <ThemedText style={styles.subtitle}>
            Cross-chain asset overview
          </ThemedText>
        </View>

        {/* Total Portfolio Value */}
        <View style={styles.section}>
          <View style={styles.totalCard}>
            <ThemedText type="title" style={styles.totalValue}>
              {totalPortfolioValue}
            </ThemedText>
            <ThemedText style={styles.totalLabel}>
              Total Portfolio Value
            </ThemedText>

            <View style={styles.portfolioStats}>
              <View style={styles.statItem}>
                <ThemedText style={styles.statValue}>
                  {portfolioStats.totalAssets}
                </ThemedText>
                <ThemedText style={styles.statLabel}>Assets</ThemedText>
              </View>
              <View style={styles.statItem}>
                <ThemedText style={styles.statValue}>
                  {portfolioStats.totalChains}
                </ThemedText>
                <ThemedText style={styles.statLabel}>Chains</ThemedText>
              </View>
              <View style={styles.statItem}>
                <ThemedText style={styles.statValue}>+12.5%</ThemedText>
                <ThemedText style={styles.statLabel}>24h Change</ThemedText>
              </View>
            </View>
          </View>
        </View>

        {/* Chain Distribution */}
        <View style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>
            Chain Distribution
          </ThemedText>

          {chainValues.map(({ chain, totalValue, assets }) => (
            <View key={chain} style={styles.chainCard}>
              <View style={styles.chainHeader}>
                <View style={styles.chainInfo}>
                  <Text style={styles.chainIcon}>{getChainIcon(chain)}</Text>
                  <View>
                    <ThemedText style={styles.chainName}>{chain}</ThemedText>
                    <ThemedText style={styles.chainAssetCount}>
                      {assets.length} asset{assets.length !== 1 ? "s" : ""}
                    </ThemedText>
                  </View>
                </View>
                <View style={styles.chainValue}>
                  <ThemedText style={styles.chainValueText}>
                    ${totalValue.toLocaleString()}
                  </ThemedText>
                  <ThemedText style={styles.chainPercentage}>
                    {(
                      (totalValue /
                        parseFloat(
                          totalPortfolioValue.replace("$", "").replace(",", "")
                        )) *
                      100
                    ).toFixed(1)}
                    %
                  </ThemedText>
                </View>
              </View>

              <View style={styles.chainAssets}>
                {assets.map((asset: Asset) => (
                  <View
                    key={`${asset.symbol}-${asset.chain}`}
                    style={styles.assetRow}
                  >
                    <View style={styles.assetInfo}>
                      <ThemedText style={styles.assetSymbol}>
                        {asset.symbol}
                      </ThemedText>
                      <ThemedText style={styles.assetName}>
                        {asset.name}
                      </ThemedText>
                    </View>
                    <View style={styles.assetBalances}>
                      <ThemedText style={styles.assetValue}>
                        {asset.value}
                      </ThemedText>
                      <ThemedText style={styles.assetBalance}>
                        {asset.balance}
                      </ThemedText>
                    </View>
                  </View>
                ))}
              </View>
            </View>
          ))}
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>
            Quick Actions
          </ThemedText>

          <View style={styles.actionsGrid}>
            <TouchableOpacity style={styles.actionCard}>
              <Text style={styles.actionIcon}>💱</Text>
              <ThemedText style={styles.actionTitle}>Swap</ThemedText>
              <ThemedText style={styles.actionSubtitle}>
                Exchange tokens
              </ThemedText>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionCard}>
              <Text style={styles.actionIcon}>🌉</Text>
              <ThemedText style={styles.actionTitle}>Bridge</ThemedText>
              <ThemedText style={styles.actionSubtitle}>
                Cross-chain transfer
              </ThemedText>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionCard}>
              <Text style={styles.actionIcon}>💎</Text>
              <ThemedText style={styles.actionTitle}>Stake</ThemedText>
              <ThemedText style={styles.actionSubtitle}>
                Earn rewards
              </ThemedText>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionCard}>
              <Text style={styles.actionIcon}>📊</Text>
              <ThemedText style={styles.actionTitle}>Analytics</ThemedText>
              <ThemedText style={styles.actionSubtitle}>
                Detailed insights
              </ThemedText>
            </TouchableOpacity>
          </View>
        </View>

        {/* Performance Metrics */}
        <View style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>
            Performance
          </ThemedText>

          <View style={styles.performanceCard}>
            <View style={styles.performanceRow}>
              <ThemedText style={styles.performanceLabel}>
                24h Change:
              </ThemedText>
              <ThemedText style={[styles.performanceValue, styles.positive]}>
                +$1,245.30 (+12.5%)
              </ThemedText>
            </View>

            <View style={styles.performanceRow}>
              <ThemedText style={styles.performanceLabel}>
                7d Change:
              </ThemedText>
              <ThemedText style={[styles.performanceValue, styles.positive]}>
                +$2,890.15 (+38.2%)
              </ThemedText>
            </View>

            <View style={styles.performanceRow}>
              <ThemedText style={styles.performanceLabel}>
                30d Change:
              </ThemedText>
              <ThemedText style={[styles.performanceValue, styles.negative]}>
                -$456.20 (-4.2%)
              </ThemedText>
            </View>

            <View style={styles.performanceRow}>
              <ThemedText style={styles.performanceLabel}>All Time:</ThemedText>
              <ThemedText style={[styles.performanceValue, styles.positive]}>
                +$8,234.67 (+367.8%)
              </ThemedText>
            </View>
          </View>
        </View>

        {/* AI Insights */}
        <View style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>
            AI Portfolio Insights
          </ThemedText>

          <View style={styles.insightCard}>
            <View style={styles.insightHeader}>
              <Text style={styles.insightIcon}>🤖</Text>
              <ThemedText style={styles.insightTitle}>
                Portfolio Analysis
              </ThemedText>
            </View>

            <ThemedText style={styles.insightText}>
              Your portfolio shows strong diversification across 4 chains. ETH
              allocation (84%) suggests bullish sentiment. Consider rebalancing
              to reduce concentration risk. AI recommends 5-10% allocation to
              Layer 2 tokens for gas optimization.
            </ThemedText>

            <View style={styles.insightActions}>
              <TouchableOpacity style={styles.insightButton}>
                <ThemedText style={styles.insightButtonText}>
                  View Details
                </ThemedText>
              </TouchableOpacity>
              <TouchableOpacity style={styles.insightButton}>
                <ThemedText style={styles.insightButtonText}>
                  Auto-Rebalance
                </ThemedText>
              </TouchableOpacity>
            </View>
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
  totalCard: {
    ...CommonStyles.card,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
    padding: 24,
    alignItems: "center",
  },
  totalValue: {
    color: AppColors.success,
    marginBottom: 8,
    fontSize: 32,
    fontWeight: "700",
  },
  totalLabel: {
    color: AppColors.textSecondary,
    marginBottom: 20,
    fontSize: 16,
  },
  portfolioStats: {
    flexDirection: "row",
    justifyContent: "space-around",
    width: "100%",
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
  },
  chainCard: {
    ...CommonStyles.card,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
  },
  chainHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  chainInfo: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  chainIcon: {
    fontSize: 24,
  },
  chainName: {
    color: AppColors.textPrimary,
    fontSize: 16,
    fontWeight: "600",
  },
  chainAssetCount: {
    color: AppColors.textMuted,
    fontSize: 12,
    marginTop: 2,
  },
  chainValue: {
    alignItems: "flex-end",
  },
  chainValueText: {
    color: AppColors.textPrimary,
    fontSize: 16,
    fontWeight: "600",
  },
  chainPercentage: {
    color: AppColors.textMuted,
    fontSize: 12,
    marginTop: 2,
  },
  chainAssets: {
    gap: 12,
  },
  assetRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: AppColors.divider,
  },
  assetInfo: {
    flex: 1,
  },
  assetSymbol: {
    color: AppColors.textPrimary,
    fontSize: 14,
    fontWeight: "600",
  },
  assetName: {
    color: AppColors.textMuted,
    fontSize: 12,
    marginTop: 2,
  },
  assetBalances: {
    alignItems: "flex-end",
  },
  assetValue: {
    color: AppColors.textPrimary,
    fontSize: 14,
    fontWeight: "600",
  },
  assetBalance: {
    color: AppColors.textMuted,
    fontSize: 12,
    marginTop: 2,
  },
  actionsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
  },
  actionCard: {
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
    width: "48%",
  },
  actionIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  actionTitle: {
    color: AppColors.textPrimary,
    fontSize: 14,
    fontWeight: "600",
    marginBottom: 4,
  },
  actionSubtitle: {
    color: AppColors.textSecondary,
    fontSize: 12,
    textAlign: "center",
  },
  performanceCard: {
    ...CommonStyles.card,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
  },
  performanceRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  performanceLabel: {
    color: AppColors.textSecondary,
    fontSize: 14,
  },
  performanceValue: {
    color: AppColors.textPrimary,
    fontSize: 14,
    fontWeight: "600",
  },
  positive: {
    color: AppColors.success,
  },
  negative: {
    color: AppColors.error,
  },
  insightCard: {
    ...CommonStyles.card,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
    borderLeftWidth: 4,
    borderLeftColor: AppColors.primary,
  },
  insightHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    marginBottom: 12,
  },
  insightIcon: {
    fontSize: 20,
  },
  insightTitle: {
    color: AppColors.textPrimary,
    fontSize: 16,
    fontWeight: "600",
  },
  insightText: {
    color: AppColors.textSecondary,
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 16,
  },
  insightActions: {
    flexDirection: "row",
    gap: 12,
  },
  insightButton: {
    backgroundColor: AppColors.primary,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  insightButtonText: {
    color: AppColors.textInverse,
    fontSize: 12,
    fontWeight: "600",
  },
});
