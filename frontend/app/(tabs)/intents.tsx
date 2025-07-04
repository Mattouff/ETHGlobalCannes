import { ThemedText } from "@/components/ThemedText";
import { ThemedView } from "@/components/ThemedView";
import { AppColors, CommonStyles } from "@/constants/AppStyles";
import { useApp } from "@/contexts/AppContext";
import {
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

export default function IntentsScreen() {
  const { state, approveIntent, rejectIntent } = useApp();

  const handleApprove = (intentId: string) => {
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
  };

  const handleReject = (intentId: string) => {
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
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending":
        return "#F59E0B";
      case "approved":
        return "#10B981";
      case "rejected":
        return "#EF4444";
      case "executed":
        return "#8B5CF6";
      default:
        return "#6B7280";
    }
  };

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

  const formatTime = (timestamp: number) => {
    const minutes = Math.floor((Date.now() - timestamp) / 60000);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  const pendingIntents = state.intents.filter(
    (intent) => intent.status === "pending"
  );
  const completedIntents = state.intents.filter(
    (intent) => intent.status !== "pending"
  );

  return (
    <ThemedView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <ThemedText type="title">AI Intents</ThemedText>
          <ThemedText style={styles.subtitle}>
            Review and manage AI-generated trading recommendations
          </ThemedText>
        </View>

        {/* Pending Intents */}
        {pendingIntents.length > 0 && (
          <View style={styles.section}>
            <ThemedText type="subtitle" style={styles.sectionTitle}>
              Pending Review ({pendingIntents.length})
            </ThemedText>

            {pendingIntents.map((intent) => (
              <View key={intent.id} style={styles.intentCard}>
                <View style={styles.intentHeader}>
                  <View style={styles.intentMeta}>
                    <Text style={styles.typeIcon}>
                      {getTypeIcon(intent.type)}
                    </Text>
                    <View>
                      <ThemedText style={styles.intentType}>
                        {intent.type.toUpperCase()}
                      </ThemedText>
                      <ThemedText style={styles.intentTime}>
                        {formatTime(intent.timestamp)}
                      </ThemedText>
                    </View>
                  </View>
                  <View style={styles.confidenceBadge}>
                    <Text style={styles.confidenceText}>
                      {Math.round(intent.confidence * 100)}%
                    </Text>
                  </View>
                </View>

                <View style={styles.tradeDetails}>
                  <View style={styles.tradeRow}>
                    <ThemedText style={styles.tradeLabel}>Amount:</ThemedText>
                    <ThemedText style={styles.tradeValue}>
                      {intent.amount} {intent.fromToken}
                    </ThemedText>
                  </View>
                  <View style={styles.tradeRow}>
                    <ThemedText style={styles.tradeLabel}>To:</ThemedText>
                    <ThemedText style={styles.tradeValue}>
                      {intent.toToken} ({intent.toChain})
                    </ThemedText>
                  </View>
                  <View style={styles.tradeRow}>
                    <ThemedText style={styles.tradeLabel}>Est. Gas:</ThemedText>
                    <ThemedText style={styles.tradeValue}>
                      {intent.estimatedGas} ETH
                    </ThemedText>
                  </View>
                </View>

                <View style={styles.reasoning}>
                  <ThemedText style={styles.reasoningLabel}>
                    AI Reasoning:
                  </ThemedText>
                  <ThemedText style={styles.reasoningText}>
                    {intent.reasoning}
                  </ThemedText>
                </View>

                <View style={styles.actionButtons}>
                  <TouchableOpacity
                    style={[styles.actionButton, styles.rejectButton]}
                    onPress={() => handleReject(intent.id)}
                  >
                    <Text style={styles.rejectButtonText}>Reject</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.actionButton, styles.approveButton]}
                    onPress={() => handleApprove(intent.id)}
                  >
                    <Text style={styles.approveButtonText}>Approve</Text>
                  </TouchableOpacity>
                </View>
              </View>
            ))}
          </View>
        )}

        {/* No Pending Intents */}
        {pendingIntents.length === 0 && (
          <View style={styles.section}>
            <View style={styles.emptyState}>
              <Text style={styles.emptyIcon}>🤖</Text>
              <ThemedText type="subtitle" style={styles.emptyTitle}>
                No Pending Intents
              </ThemedText>
              <ThemedText style={styles.emptySubtitle}>
                Your AI agent is monitoring the markets. New opportunities will
                appear here when detected.
              </ThemedText>
            </View>
          </View>
        )}

        {/* Recent Activity */}
        {completedIntents.length > 0 && (
          <View style={styles.section}>
            <ThemedText type="subtitle" style={styles.sectionTitle}>
              Recent Activity
            </ThemedText>

            {completedIntents.slice(0, 5).map((intent) => (
              <View key={intent.id} style={styles.historyCard}>
                <View style={styles.historyHeader}>
                  <View style={styles.historyMeta}>
                    <Text style={styles.typeIcon}>
                      {getTypeIcon(intent.type)}
                    </Text>
                    <View>
                      <ThemedText style={styles.historyType}>
                        {intent.type.toUpperCase()}
                      </ThemedText>
                      <ThemedText style={styles.historyTime}>
                        {formatTime(intent.timestamp)}
                      </ThemedText>
                    </View>
                  </View>
                  <View
                    style={[
                      styles.statusBadge,
                      { backgroundColor: getStatusColor(intent.status) },
                    ]}
                  >
                    <Text style={styles.statusText}>
                      {intent.status.toUpperCase()}
                    </Text>
                  </View>
                </View>

                <ThemedText style={styles.historyDetails}>
                  {intent.amount} {intent.fromToken} → {intent.toToken}
                </ThemedText>
              </View>
            ))}
          </View>
        )}

        {/* Agent Settings */}
        <View style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>
            Agent Settings
          </ThemedText>
          <View style={styles.settingsCard}>
            <View style={styles.settingRow}>
              <ThemedText style={styles.settingLabel}>
                Auto-approve threshold:
              </ThemedText>
              <ThemedText style={styles.settingValue}>95%</ThemedText>
            </View>
            <View style={styles.settingRow}>
              <ThemedText style={styles.settingLabel}>
                Max trade amount:
              </ThemedText>
              <ThemedText style={styles.settingValue}>1 ETH</ThemedText>
            </View>
            <View style={styles.settingRow}>
              <ThemedText style={styles.settingLabel}>
                Risk tolerance:
              </ThemedText>
              <ThemedText style={styles.settingValue}>Moderate</ThemedText>
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
  intentCard: {
    ...CommonStyles.card,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.intentPending,
  },
  intentHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  intentMeta: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  typeIcon: {
    fontSize: 24,
  },
  intentType: {
    color: AppColors.textPrimary,
    fontSize: 14,
    fontWeight: "600",
  },
  intentTime: {
    color: AppColors.textMuted,
    fontSize: 12,
    marginTop: 2,
  },
  confidenceBadge: {
    backgroundColor: AppColors.success,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  confidenceText: {
    color: AppColors.textInverse,
    fontSize: 12,
    fontWeight: "600",
  },
  tradeDetails: {
    marginBottom: 16,
  },
  tradeRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 8,
  },
  tradeLabel: {
    color: AppColors.textSecondary,
    fontSize: 14,
  },
  tradeValue: {
    color: AppColors.textPrimary,
    fontSize: 14,
    fontWeight: "600",
  },
  reasoning: {
    marginBottom: 20,
  },
  reasoningLabel: {
    color: AppColors.textPrimary,
    fontSize: 14,
    fontWeight: "600",
    marginBottom: 8,
  },
  reasoningText: {
    color: AppColors.textSecondary,
    fontSize: 14,
    lineHeight: 20,
  },
  actionButtons: {
    flexDirection: "row",
    gap: 12,
  },
  actionButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: "center",
  },
  rejectButton: {
    backgroundColor: AppColors.error,
  },
  approveButton: {
    backgroundColor: AppColors.success,
  },
  rejectButtonText: {
    color: AppColors.textInverse,
    fontSize: 14,
    fontWeight: "600",
  },
  approveButtonText: {
    color: AppColors.textInverse,
    fontSize: 14,
    fontWeight: "600",
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
  historyCard: {
    ...CommonStyles.card,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
    padding: 16,
    marginBottom: 12,
  },
  historyHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  historyMeta: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  historyType: {
    color: AppColors.textPrimary,
    fontSize: 12,
    fontWeight: "600",
  },
  historyTime: {
    color: AppColors.textMuted,
    fontSize: 10,
    marginTop: 2,
  },
  statusBadge: {
    ...CommonStyles.statusBadge,
  },
  statusText: {
    ...CommonStyles.statusBadgeText,
  },
  historyDetails: {
    color: AppColors.textSecondary,
    fontSize: 14,
    fontWeight: "500",
  },
  settingsCard: {
    ...CommonStyles.card,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
  },
  settingRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 12,
  },
  settingLabel: {
    color: AppColors.textSecondary,
    fontSize: 14,
  },
  settingValue: {
    color: AppColors.textPrimary,
    fontSize: 14,
    fontWeight: "600",
  },
});
