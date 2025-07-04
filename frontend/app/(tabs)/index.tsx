import { ThemedText } from "@/components/ThemedText";
import { ThemedView } from "@/components/ThemedView";
import { useApp } from "@/contexts/AppContext";
import { useWallet } from "@/contexts/WalletContext";
import { useEffect } from "react";
import {
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

export default function DashboardScreen() {
  const { state } = useApp();
  const { isConnected, address, connect, isConnecting, disconnect } =
    useWallet();

  // Connect wallet to app context when wallet connects
  useEffect(() => {
    if (isConnected && address) {
      // In a real app, you would get the chain from the wallet
      // For demo, assume Ethereum mainnet
      // connectWallet(address, 'Ethereum');
    }
  }, [isConnected, address]);

  const handleConnectWallet = async () => {
    try {
      await connect();
    } catch {
      Alert.alert("Connection Error", "Failed to connect wallet");
    }
  };

  const handleDisconnectWallet = async () => {
    try {
      await disconnect();
    } catch {
      Alert.alert("Disconnection Error", "Failed to disconnect wallet");
    }
  };

  const formatAddress = (addr: string) => {
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
  };

  const getStatusColor = (isActive: boolean) => {
    return isActive ? "#10B981" : "#EF4444";
  };

  if (!isConnected) {
    return (
      <ThemedView style={styles.container}>
        <View style={styles.connectContainer}>
          <ThemedText type="title" style={styles.title}>
            AI Agent Cross-Chain Portfolio
          </ThemedText>
          <ThemedText style={styles.subtitle}>
            Connect your wallet to start managing your cross-chain assets with
            AI assistance
          </ThemedText>

          <TouchableOpacity
            style={[
              styles.connectButton,
              isConnecting && styles.connectingButton,
            ]}
            onPress={handleConnectWallet}
            disabled={isConnecting}
          >
            <Text style={styles.connectButtonText}>
              {isConnecting ? "Connecting..." : "Connect Wallet"}
            </Text>
          </TouchableOpacity>

          <View style={styles.featuresContainer}>
            <View style={styles.feature}>
              <Text style={styles.featureIcon}>🤖</Text>
              <ThemedText style={styles.featureText}>
                AI-powered trading insights
              </ThemedText>
            </View>
            <View style={styles.feature}>
              <Text style={styles.featureIcon}>🌐</Text>
              <ThemedText style={styles.featureText}>
                Cross-chain asset management
              </ThemedText>
            </View>
            <View style={styles.feature}>
              <Text style={styles.featureIcon}>⚡</Text>
              <ThemedText style={styles.featureText}>
                Automated execution
              </ThemedText>
            </View>
          </View>
        </View>
      </ThemedView>
    );
  }

  return (
    <ThemedView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <ThemedText type="title">Dashboard</ThemedText>
            <Text style={styles.address}>{formatAddress(address!)}</Text>
          </View>
          <TouchableOpacity
            style={styles.disconnectButton}
            onPress={handleDisconnectWallet}
          >
            <Text style={styles.disconnectButtonText}>Disconnect</Text>
          </TouchableOpacity>
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
  },
  connectContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 24,
  },
  title: {
    textAlign: "center",
    marginBottom: 16,
  },
  subtitle: {
    textAlign: "center",
    marginBottom: 32,
    opacity: 0.7,
  },
  connectButton: {
    backgroundColor: "#007AFF",
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
    marginBottom: 32,
  },
  connectingButton: {
    opacity: 0.6,
  },
  connectButtonText: {
    color: "white",
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
    color: "#666",
    marginTop: 4,
  },
  disconnectButton: {
    backgroundColor: "#EF4444",
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  disconnectButtonText: {
    color: "white",
    fontSize: 14,
    fontWeight: "600",
  },
  section: {
    padding: 24,
    paddingTop: 0,
  },
  sectionTitle: {
    marginBottom: 16,
  },
  portfolioCard: {
    backgroundColor: "#FFFFFF",
    padding: 24,
    borderRadius: 16,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#E2E8F0",
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  portfolioValue: {
    color: "#059669",
    marginBottom: 8,
  },
  portfolioLabel: {
    color: "#4A5568",
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
    color: "#1A202C",
  },
  statLabel: {
    fontSize: 12,
    color: "#4A5568",
    marginTop: 4,
  },
  agentCard: {
    backgroundColor: "#FFFFFF",
    padding: 20,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
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
    color: "#1A202C",
  },
  confidenceText: {
    fontSize: 14,
    color: "#059669",
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
    color: "#1A202C",
  },
  metricLabel: {
    fontSize: 12,
    color: "#4A5568",
    marginTop: 4,
  },
  intentCard: {
    backgroundColor: "#FFFFFF",
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 3,
  },
  intentHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  intentType: {
    backgroundColor: "#0066CC",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  intentTypeText: {
    color: "white",
    fontSize: 10,
    fontWeight: "600",
  },
  intentStatus: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  intentStatusText: {
    color: "white",
    fontSize: 10,
    fontWeight: "600",
  },
  intentDetails: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 8,
  },
  intentReasoning: {
    fontSize: 14,
    opacity: 0.7,
    marginBottom: 12,
  },
  intentFooter: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  intentConfidence: {
    fontSize: 12,
    color: "#10B981",
    fontWeight: "600",
  },
  intentTime: {
    fontSize: 12,
    opacity: 0.7,
  },
  quickActions: {
    flexDirection: "row",
    justifyContent: "space-around",
  },
  actionButton: {
    alignItems: "center",
    padding: 16,
    backgroundColor: "#F8F9FA",
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
  },
});
