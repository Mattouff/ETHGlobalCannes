import { ThemedText } from "@/components/ThemedText";
import { ThemedView } from "@/components/ThemedView";
import { AppColors, CommonStyles } from "@/constants/AppStyles";
import { useApp } from "@/contexts/AppContext";
import { useAccount, useConnect, useDisconnect } from "wagmi";
import {
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

export default function DashboardScreen() {
  const { state } = useApp();
  const { address, isConnected } = useAccount();
  const { connect, connectors, isPending } = useConnect();
  const { disconnect } = useDisconnect();

  const formatAddress = (addr: string) => {
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
  };

  const handleConnect = () => {
    // Utilise le premier connecteur disponible (WalletConnect ou MetaMask)
    const connector = connectors[0];
    if (connector) {
      connect({ connector });
    }
  };

  const getStatusColor = (isActive: boolean) => {
    return isActive ? "#10B981" : "#EF4444";
  };

  return (
    <ThemedView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={CommonStyles.header}>
          <View>
            <ThemedText style={CommonStyles.headerTitle}>Dashboard</ThemedText>
            {/* <Text style={styles.address}>{formatAddress(address!)}</Text> */}
          </View>
        </View>

        {/* Portfolio Overview */}
        <View style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>
            Portfolio Overview
          </ThemedText>
          <View style={styles.portfolioCard}>
            <ThemedText type="title" style={styles.portfolioValue}>
              {state.totalPortfolioValue}
            </ThemedText>
            <ThemedText style={styles.portfolioLabel}>Total Value</ThemedText>
            <View style={styles.portfolioStats}>
              <View style={styles.stat}>
                <ThemedText style={styles.statValue}>
                  {state.assets.length}
                </ThemedText>
                <ThemedText style={styles.statLabel}>Assets</ThemedText>
              </View>
              <View style={styles.stat}>
                <ThemedText style={styles.statValue}>4</ThemedText>
                <ThemedText style={styles.statLabel}>Chains</ThemedText>
              </View>
            </View>
          </View>
        </View>

        {/* AI Agent Status */}
        <View style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>
            AI Agent Status
          </ThemedText>
          
          <View style={styles.agentCard}>
            <View style={styles.agentHeader}>
              <View style={styles.agentStatus}>
                <View
                  style={[
                    styles.statusDot,
                    {
                      backgroundColor: getStatusColor(
                        state.agentStatus.isActive
                      ),
                    },
                  ]}
                />
                <ThemedText style={styles.statusText}>
                  {state.agentStatus.isActive ? "Active" : "Inactive"}
                </ThemedText>
              </View>
              <ThemedText style={styles.confidenceText}>
                {Math.round(state.agentStatus.confidenceLevel * 100)}%
                Confidence
              </ThemedText>
            </View>

            <View style={styles.agentMetrics}>
              <View style={styles.metric}>
                <ThemedText style={styles.metricValue}>
                  {state.agentStatus.marketDataSources.length}
                </ThemedText>
                <ThemedText style={styles.metricLabel}>Data Sources</ThemedText>
              </View>
              <View style={styles.metric}>
                <ThemedText style={styles.metricValue}>
                  {state.agentStatus.newsSourcesActive}
                </ThemedText>
                <ThemedText style={styles.metricLabel}>News Sources</ThemedText>
              </View>
              <View style={styles.metric}>
                <ThemedText style={styles.metricValue}>
                  {Math.floor(
                    (Date.now() - state.agentStatus.lastUpdate) / 60000
                  )}
                  m
                </ThemedText>
                <ThemedText style={styles.metricLabel}>Last Update</ThemedText>
              </View>
            </View>
          </View>
        </View>

        {/* Recent Intents */}
        <View style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>
            Recent AI Intents
          </ThemedText>
          {state.intents.slice(0, 3).map((intent) => (
            <View key={intent.id} style={styles.intentCard}>
              <View style={styles.intentHeader}>
                <View style={styles.intentType}>
                  <Text style={styles.intentTypeText}>
                    {intent.type.toUpperCase()}
                  </Text>
                </View>
                <View
                  style={[
                    styles.intentStatus,
                    {
                      backgroundColor:
                        intent.status === "pending" ? "#F59E0B" : "#10B981",
                    },
                  ]}
                >
                  <Text style={styles.intentStatusText}>
                    {intent.status.toUpperCase()}
                  </Text>
                </View>
              </View>

              <ThemedText style={styles.intentDetails}>
                {intent.amount} {intent.fromToken} → {intent.toToken}
              </ThemedText>

              <ThemedText style={styles.intentReasoning} numberOfLines={2}>
                {intent.reasoning}
              </ThemedText>

              <View style={styles.intentFooter}>
                <ThemedText style={styles.intentConfidence}>
                  {Math.round(intent.confidence * 100)}% Confidence
                </ThemedText>
                <ThemedText style={styles.intentTime}>
                  {Math.floor((Date.now() - intent.timestamp) / 60000)}m ago
                </ThemedText>
              </View>
            </View>
          ))}
        </View>

        {/* Wallet Connection */}
        <View style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>
            Wallet Connection
          </ThemedText>
          <View style={styles.walletSection}>
            {!isConnected ? (
              <TouchableOpacity 
                style={[styles.connectButton, isPending && styles.connectingButton]}
                onPress={handleConnect}
                disabled={isPending}
              >
                <Text style={styles.connectButtonText}>
                  {isPending ? "Connecting..." : "Connect Wallet"}
                </Text>
              </TouchableOpacity>
            ) : (
              <View style={styles.connectedInfo}>
                <Text style={styles.walletAddress}>
                  Connected: {formatAddress(address!)}
                </Text>
                <TouchableOpacity 
                  style={styles.disconnectButton} 
                  onPress={() => disconnect()}
                >
                  <Text style={styles.disconnectButtonText}>
                    Disconnect
                  </Text>
                </TouchableOpacity>
              </View>
            )}
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
              <ThemedText style={styles.actionText}>View Portfolio</ThemedText>
            </TouchableOpacity>
            <TouchableOpacity style={styles.actionButton}>
              <Text style={styles.actionIcon}>🎯</Text>
              <ThemedText style={styles.actionText}>Review Intents</ThemedText>
            </TouchableOpacity>
            <TouchableOpacity style={styles.actionButton}>
              <Text style={styles.actionIcon}>📜</Text>
              <ThemedText style={styles.actionText}>
                Transaction History
              </ThemedText>
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
  connectContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 24,
  },
  title: {
    color: AppColors.textPrimary,
    textAlign: "center",
    marginBottom: 16,
  },
  subtitle: {
    color: AppColors.textSecondary,
    textAlign: "center",
    marginBottom: 32,
    lineHeight: 20,
  },
  connectButton: {
    backgroundColor: AppColors.primary,
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
    marginBottom: 32,
  },
  connectingButton: {
    opacity: 0.6,
  },
  connectButtonText: {
    color: AppColors.textInverse,
    fontSize: 16,
    fontWeight: "600",
  },
  featuresContainer: {
    gap: 16,
  },
  feature: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  featureIcon: {
    fontSize: 24,
  },
  featureText: {
    color: AppColors.textPrimary,
    fontSize: 16,
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 24,
    paddingTop: 60,
  },
  address: {
    fontSize: 14,
    color: AppColors.textSecondary,
    marginTop: 4,
  },
  disconnectButton: {
    backgroundColor: AppColors.error,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  disconnectButtonText: {
    color: AppColors.textInverse,
    fontSize: 14,
    fontWeight: "600",
  },
  section: {
    ...CommonStyles.section,
  },
  sectionTitle: {
    ...CommonStyles.sectionTitle,
  },
  portfolioCard: {
    ...CommonStyles.card,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
    padding: 24,
    alignItems: "center",
  },
  portfolioValue: {
    color: AppColors.success,
    marginBottom: 8,
  },
  portfolioLabel: {
    color: AppColors.textSecondary,
    marginBottom: 16,
  },
  portfolioStats: {
    flexDirection: "row",
    gap: 32,
  },
  stat: {
    alignItems: "center",
  },
  statValue: {
    fontSize: 20,
    fontWeight: "600",
    color: AppColors.textPrimary,
  },
  statLabel: {
    fontSize: 12,
    color: AppColors.textMuted,
    marginTop: 4,
  },
  agentCard: {
    ...CommonStyles.card,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
  },
  agentHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  agentStatus: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  statusText: {
    fontWeight: "600",
    color: AppColors.textPrimary,
  },
  confidenceText: {
    fontSize: 14,
    color: AppColors.success,
    fontWeight: "600",
  },
  agentMetrics: {
    flexDirection: "row",
    justifyContent: "space-around",
  },
  metric: {
    alignItems: "center",
  },
  metricValue: {
    fontSize: 18,
    fontWeight: "600",
    color: AppColors.textPrimary,
  },
  metricLabel: {
    fontSize: 12,
    color: AppColors.textMuted,
    marginTop: 4,
  },
  intentCard: {
    ...CommonStyles.card,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
    padding: 16,
    marginBottom: 12,
  },
  intentHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  intentType: {
    backgroundColor: AppColors.primary,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  intentTypeText: {
    color: AppColors.textInverse,
    fontSize: 10,
    fontWeight: "600",
  },
  intentStatus: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  intentStatusText: {
    color: AppColors.textInverse,
    fontSize: 10,
    fontWeight: "600",
  },
  intentDetails: {
    fontSize: 16,
    fontWeight: "600",
    color: AppColors.textPrimary,
    marginBottom: 8,
  },
  intentReasoning: {
    fontSize: 14,
    color: AppColors.textSecondary,
    marginBottom: 12,
    lineHeight: 18,
  },
  intentFooter: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  intentConfidence: {
    fontSize: 12,
    color: AppColors.success,
    fontWeight: "600",
  },
  intentTime: {
    fontSize: 12,
    color: AppColors.textMuted,
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
    fontSize: 24,
    marginBottom: 8,
  },
  actionText: {
    fontSize: 12,
    textAlign: "center",
    color: AppColors.textPrimary,
  },
  walletSection: {
    alignItems: "center",
    padding: 16,
    gap: 12,
  },
  connectedInfo: {
    alignItems: "center",
    gap: 8,
  },
  walletAddress: {
    fontSize: 14,
    color: AppColors.textSecondary,
    backgroundColor: AppColors.cardBackground,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: AppColors.border,
  },
});
