import { ThemedText } from "@/components/ThemedText";
import { AppColors, CommonStyles } from "@/constants/AppStyles";
import { useIntentActions } from "@/src/hooks";
import { Intent } from "@/src/types";
import {
  formatTimeAgo,
  getStatusColor,
  getTypeIcon,
} from "@/src/utils/helpers";
import {
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

export default function IntentsScreen() {
  const {
    handleApproveIntent,
    handleRejectIntent,
    getPendingIntents,
    getCompletedIntents,
  } = useIntentActions();

  const pendingIntents = getPendingIntents();
  const completedIntents = getCompletedIntents();

  const renderIntentCard = (intent: Intent, showActions = false) => (
    <View key={intent.id} style={styles.intentCard}>
      {/* Intent Header */}
      <View style={styles.intentHeader}>
        <View style={styles.intentTypeRow}>
          <Text style={styles.typeIcon}>{getTypeIcon(intent.type)}</Text>
          <Text style={styles.intentType}>
            {intent.type.charAt(0).toUpperCase() + intent.type.slice(1)}
          </Text>
          <View
            style={[
              styles.statusBadge,
              { backgroundColor: getStatusColor(intent.status) },
            ]}
          >
            <Text style={styles.statusText}>{intent.status}</Text>
          </View>
        </View>
        <Text style={styles.timestamp}>{formatTimeAgo(intent.timestamp)}</Text>
      </View>

      {/* Intent Details */}
      <View style={styles.intentDetails}>
        <View style={styles.tokenRow}>
          <Text style={styles.tokenInfo}>
            {intent.amount} {intent.fromToken}
          </Text>
          <Text style={styles.arrow}>→</Text>
          <Text style={styles.tokenInfo}>{intent.toToken}</Text>
        </View>

        <View style={styles.chainRow}>
          <Text style={styles.chainInfo}>{intent.fromChain}</Text>
          {intent.fromChain !== intent.toChain && (
            <>
              <Text style={styles.arrow}>→</Text>
              <Text style={styles.chainInfo}>{intent.toChain}</Text>
            </>
          )}
        </View>

        <View style={styles.gasRow}>
          <Text style={styles.gasLabel}>Est. Gas:</Text>
          <Text style={styles.gasValue}>{intent.estimatedGas} ETH</Text>
        </View>

        <View style={styles.confidenceRow}>
          <Text style={styles.confidenceLabel}>Confidence:</Text>
          <Text style={styles.confidenceValue}>
            {Math.round(intent.confidence * 100)}%
          </Text>
        </View>
      </View>

      {/* AI Reasoning */}
      <View style={styles.reasoningSection}>
        <Text style={styles.reasoningLabel}>🤖 AI Analysis:</Text>
        <Text style={styles.reasoningText}>{intent.reasoning}</Text>
      </View>

      {/* Action Buttons */}
      {showActions && intent.status === "pending" && (
        <View style={styles.actionButtons}>
          <TouchableOpacity
            style={[styles.actionButton, styles.rejectButton]}
            onPress={() => handleRejectIntent(intent.id)}
          >
            <Text style={styles.rejectButtonText}>Reject</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.actionButton, styles.approveButton]}
            onPress={() => handleApproveIntent(intent.id)}
          >
            <Text style={styles.approveButtonText}>Approve</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={CommonStyles.header}>
          <ThemedText style={CommonStyles.headerTitle}>
            Trading Intents
          </ThemedText>
          <ThemedText style={CommonStyles.headerSubtitle}>
            AI-powered trading recommendations based on market analysis
          </ThemedText>
        </View>

        {/* Pending Intents */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>
              ⏳ Pending Approval ({pendingIntents.length})
            </Text>
          </View>

          {pendingIntents.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptyIcon}>✨</Text>
              <Text style={styles.emptyTitle}>No Pending Intents</Text>
              <Text style={styles.emptySubtitle}>
                The AI agent will notify you when new trading opportunities are
                detected
              </Text>
            </View>
          ) : (
            pendingIntents.map((intent: Intent) =>
              renderIntentCard(intent, true)
            )
          )}
        </View>

        {/* Recent Intents */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>
              📊 Recent Activity ({completedIntents.length})
            </Text>
          </View>

          {completedIntents.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptyIcon}>📈</Text>
              <Text style={styles.emptyTitle}>No Recent Activity</Text>
              <Text style={styles.emptySubtitle}>
                Completed intents will appear here
              </Text>
            </View>
          ) : (
            completedIntents
              .slice(0, 5)
              .map((intent: Intent) => renderIntentCard(intent, false))
          )}
        </View>
      </ScrollView>
    </View>
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
  section: {
    marginBottom: 24,
  },
  sectionHeader: {
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: AppColors.textPrimary,
    marginBottom: 4,
  },
  emptyState: {
    alignItems: "center",
    paddingVertical: 32,
    paddingHorizontal: 16,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: AppColors.textPrimary,
    marginBottom: 8,
    textAlign: "center",
  },
  emptySubtitle: {
    fontSize: 14,
    color: AppColors.textSecondary,
    textAlign: "center",
    lineHeight: 20,
  },
  intentCard: {
    backgroundColor: AppColors.cardBackground,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: AppColors.border,
  },
  intentHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 12,
  },
  intentTypeRow: {
    flexDirection: "row",
    alignItems: "center",
    flex: 1,
  },
  typeIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  intentType: {
    fontSize: 16,
    fontWeight: "600",
    color: AppColors.textPrimary,
    marginRight: 12,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#FFFFFF",
    textTransform: "uppercase",
  },
  timestamp: {
    fontSize: 12,
    color: AppColors.textSecondary,
  },
  intentDetails: {
    marginBottom: 12,
  },
  tokenRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  tokenInfo: {
    fontSize: 16,
    fontWeight: "600",
    color: AppColors.textPrimary,
  },
  arrow: {
    fontSize: 16,
    color: AppColors.textSecondary,
    marginHorizontal: 12,
  },
  chainRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  chainInfo: {
    fontSize: 14,
    color: AppColors.textSecondary,
  },
  gasRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 4,
  },
  gasLabel: {
    fontSize: 14,
    color: AppColors.textSecondary,
  },
  gasValue: {
    fontSize: 14,
    fontWeight: "500",
    color: AppColors.textPrimary,
  },
  confidenceRow: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  confidenceLabel: {
    fontSize: 14,
    color: AppColors.textSecondary,
  },
  confidenceValue: {
    fontSize: 14,
    fontWeight: "600",
    color: AppColors.primary,
  },
  reasoningSection: {
    backgroundColor: AppColors.screenBackground,
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  reasoningLabel: {
    fontSize: 14,
    fontWeight: "600",
    color: AppColors.textPrimary,
    marginBottom: 6,
  },
  reasoningText: {
    fontSize: 14,
    color: AppColors.textSecondary,
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
    backgroundColor: "transparent",
    borderWidth: 1,
    borderColor: AppColors.error,
  },
  approveButton: {
    backgroundColor: AppColors.success,
  },
  rejectButtonText: {
    fontSize: 16,
    fontWeight: "600",
    color: AppColors.error,
  },
  approveButtonText: {
    fontSize: 16,
    fontWeight: "600",
    color: "#FFFFFF",
  },
});
