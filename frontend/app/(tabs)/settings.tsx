import { ThemedText } from "@/components/ThemedText";
import { ThemedView } from "@/components/ThemedView";
import { AppColors, CommonStyles } from "@/constants/AppStyles";
import { useApp } from "@/contexts/AppContext";
import { useWallet } from "@/contexts/WalletContext";
import { formatAddress } from "@/src/utils/helpers";
import { useState } from "react";
import {
  Alert,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

export default function SettingsScreen() {
  const { isConnected, address, disconnect } = useWallet();
  const { state } = useApp();

  // Settings state
  const [autoApprove, setAutoApprove] = useState(false);
  const [notifications, setNotifications] = useState(true);
  const [biometric, setBiometric] = useState(false);
  const [advancedMode, setAdvancedMode] = useState(false);

  const handleDisconnectWallet = () => {
    Alert.alert(
      "Disconnect Wallet",
      "Are you sure you want to disconnect your wallet?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Disconnect",
          style: "destructive",
          onPress: disconnect,
        },
      ]
    );
  };

  return (
    <ThemedView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <ThemedText type="title">Settings</ThemedText>
          <ThemedText style={styles.subtitle}>
            Manage your wallet and AI agent preferences
          </ThemedText>
        </View>

        {/* Wallet Section */}
        {isConnected && (
          <View style={styles.section}>
            <ThemedText type="subtitle" style={styles.sectionTitle}>
              Wallet
            </ThemedText>

            <View style={styles.walletCard}>
              <View style={styles.walletInfo}>
                <View style={styles.walletIcon}>
                  <Text style={styles.walletIconText}>🔗</Text>
                </View>
                <View style={styles.walletDetails}>
                  <ThemedText style={styles.walletLabel}>
                    Connected Wallet
                  </ThemedText>
                  <ThemedText style={styles.walletAddress}>
                    {address ? formatAddress(address) : "Not connected"}
                  </ThemedText>
                </View>
              </View>

              <TouchableOpacity
                style={styles.disconnectButton}
                onPress={handleDisconnectWallet}
              >
                <ThemedText style={styles.disconnectButtonText}>
                  Disconnect
                </ThemedText>
              </TouchableOpacity>
            </View>

            <View style={styles.networkInfo}>
              <View style={styles.networkRow}>
                <ThemedText style={styles.networkLabel}>Network:</ThemedText>
                <ThemedText style={styles.networkValue}>
                  Ethereum Mainnet
                </ThemedText>
              </View>
              <View style={styles.networkRow}>
                <ThemedText style={styles.networkLabel}>Balance:</ThemedText>
                <ThemedText style={styles.networkValue}>2.45 ETH</ThemedText>
              </View>
            </View>
          </View>
        )}

        {/* AI Agent Settings */}
        <View style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>
            AI Agent
          </ThemedText>

          <View style={styles.settingsCard}>
            <View style={styles.settingItem}>
              <View style={styles.settingInfo}>
                <ThemedText style={styles.settingLabel}>
                  Auto-approve Low Risk
                </ThemedText>
                <ThemedText style={styles.settingDescription}>
                  Automatically approve intents with 95%+ confidence
                </ThemedText>
              </View>
              <Switch
                value={autoApprove}
                onValueChange={setAutoApprove}
                trackColor={{ false: "#E5E7EB", true: "#10B981" }}
                thumbColor={autoApprove ? "#FFFFFF" : "#FFFFFF"}
              />
            </View>

            <View style={styles.settingItem}>
              <View style={styles.settingInfo}>
                <ThemedText style={styles.settingLabel}>
                  Agent Status
                </ThemedText>
                <ThemedText style={styles.settingDescription}>
                  {state.agentStatus.isActive
                    ? "Active - Monitoring markets"
                    : "Inactive"}
                </ThemedText>
              </View>
              <View
                style={[
                  styles.statusIndicator,
                  {
                    backgroundColor: state.agentStatus.isActive
                      ? "#10B981"
                      : "#EF4444",
                  },
                ]}
              />
            </View>

            <TouchableOpacity style={styles.settingButton}>
              <ThemedText style={styles.settingButtonText}>
                Configure Agent Parameters
              </ThemedText>
              <Text style={styles.chevron}>›</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Notifications */}
        <View style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>
            Notifications
          </ThemedText>

          <View style={styles.settingsCard}>
            <View style={styles.settingItem}>
              <View style={styles.settingInfo}>
                <ThemedText style={styles.settingLabel}>
                  Push Notifications
                </ThemedText>
                <ThemedText style={styles.settingDescription}>
                  Get notified about new intents and transactions
                </ThemedText>
              </View>
              <Switch
                value={notifications}
                onValueChange={setNotifications}
                trackColor={{ false: "#E5E7EB", true: "#007AFF" }}
                thumbColor={notifications ? "#FFFFFF" : "#FFFFFF"}
              />
            </View>

            <TouchableOpacity style={styles.settingButton}>
              <ThemedText style={styles.settingButtonText}>
                Notification Preferences
              </ThemedText>
              <Text style={styles.chevron}>›</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Security */}
        <View style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>
            Security
          </ThemedText>

          <View style={styles.settingsCard}>
            <View style={styles.settingItem}>
              <View style={styles.settingInfo}>
                <ThemedText style={styles.settingLabel}>
                  Biometric Authentication
                </ThemedText>
                <ThemedText style={styles.settingDescription}>
                  Use Face ID or Touch ID for app access
                </ThemedText>
              </View>
              <Switch
                value={biometric}
                onValueChange={setBiometric}
                trackColor={{ false: "#E5E7EB", true: "#007AFF" }}
                thumbColor={biometric ? "#FFFFFF" : "#FFFFFF"}
              />
            </View>

            <TouchableOpacity style={styles.settingButton}>
              <ThemedText style={styles.settingButtonText}>
                Transaction Limits
              </ThemedText>
              <Text style={styles.chevron}>›</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.settingButton}>
              <ThemedText style={styles.settingButtonText}>
                Recovery Phrase
              </ThemedText>
              <Text style={styles.chevron}>›</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Advanced */}
        <View style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>
            Advanced
          </ThemedText>

          <View style={styles.settingsCard}>
            <View style={styles.settingItem}>
              <View style={styles.settingInfo}>
                <ThemedText style={styles.settingLabel}>
                  Advanced Mode
                </ThemedText>
                <ThemedText style={styles.settingDescription}>
                  Show detailed transaction data and debug info
                </ThemedText>
              </View>
              <Switch
                value={advancedMode}
                onValueChange={setAdvancedMode}
                trackColor={{ false: "#E5E7EB", true: "#007AFF" }}
                thumbColor={advancedMode ? "#FFFFFF" : "#FFFFFF"}
              />
            </View>

            <TouchableOpacity style={styles.settingButton}>
              <ThemedText style={styles.settingButtonText}>
                Network Settings
              </ThemedText>
              <Text style={styles.chevron}>›</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.settingButton}>
              <ThemedText style={styles.settingButtonText}>
                Data Export
              </ThemedText>
              <Text style={styles.chevron}>›</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* About */}
        <View style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>
            About
          </ThemedText>

          <View style={styles.aboutCard}>
            <View style={styles.aboutRow}>
              <ThemedText style={styles.aboutLabel}>Version:</ThemedText>
              <ThemedText style={styles.aboutValue}>1.0.0</ThemedText>
            </View>

            <View style={styles.aboutRow}>
              <ThemedText style={styles.aboutLabel}>Build:</ThemedText>
              <ThemedText style={styles.aboutValue}>2024.12.20</ThemedText>
            </View>

            <View style={styles.aboutRow}>
              <ThemedText style={styles.aboutLabel}>Network:</ThemedText>
              <ThemedText style={styles.aboutValue}>Mainnet</ThemedText>
            </View>
          </View>

          <View style={styles.aboutLinks}>
            <TouchableOpacity style={styles.aboutButton}>
              <ThemedText style={styles.aboutButtonText}>
                Privacy Policy
              </ThemedText>
            </TouchableOpacity>

            <TouchableOpacity style={styles.aboutButton}>
              <ThemedText style={styles.aboutButtonText}>
                Terms of Service
              </ThemedText>
            </TouchableOpacity>

            <TouchableOpacity style={styles.aboutButton}>
              <ThemedText style={styles.aboutButtonText}>Support</ThemedText>
            </TouchableOpacity>
          </View>
        </View>

        {/* Danger Zone */}
        <View style={styles.section}>
          <ThemedText
            type="subtitle"
            style={[styles.sectionTitle, styles.dangerTitle]}
          >
            Danger Zone
          </ThemedText>

          <View style={styles.dangerCard}>
            <TouchableOpacity style={styles.dangerButton}>
              <ThemedText style={styles.dangerButtonText}>
                Reset AI Agent
              </ThemedText>
            </TouchableOpacity>

            <TouchableOpacity style={styles.dangerButton}>
              <ThemedText style={styles.dangerButtonText}>
                Clear Transaction History
              </ThemedText>
            </TouchableOpacity>

            <TouchableOpacity style={styles.dangerButton}>
              <ThemedText style={styles.dangerButtonText}>
                Delete All Data
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
  dangerTitle: {
    color: AppColors.error,
  },
  walletCard: {
    ...CommonStyles.card,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
    marginBottom: 16,
  },
  walletInfo: {
    flexDirection: "row",
    alignItems: "center",
    gap: 16,
    marginBottom: 16,
  },
  walletIcon: {
    width: 48,
    height: 48,
    backgroundColor: AppColors.primary,
    borderRadius: 24,
    alignItems: "center",
    justifyContent: "center",
  },
  walletIconText: {
    fontSize: 20,
  },
  walletDetails: {
    flex: 1,
  },
  walletLabel: {
    color: AppColors.textSecondary,
    fontSize: 14,
    marginBottom: 4,
  },
  walletAddress: {
    color: AppColors.textPrimary,
    fontSize: 16,
    fontWeight: "600",
  },
  disconnectButton: {
    backgroundColor: AppColors.error,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: "center",
  },
  disconnectButtonText: {
    color: AppColors.textInverse,
    fontSize: 14,
    fontWeight: "600",
  },
  networkInfo: {
    ...CommonStyles.card,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
    padding: 16,
  },
  networkRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 8,
  },
  networkLabel: {
    color: AppColors.textSecondary,
    fontSize: 14,
  },
  networkValue: {
    color: AppColors.textPrimary,
    fontSize: 14,
    fontWeight: "600",
  },
  settingsCard: {
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
    borderRadius: 16,
    overflow: "hidden",
  },
  settingItem: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: AppColors.divider,
  },
  settingInfo: {
    flex: 1,
    marginRight: 16,
  },
  settingLabel: {
    color: AppColors.textPrimary,
    fontSize: 16,
    fontWeight: "500",
    marginBottom: 4,
  },
  settingDescription: {
    color: AppColors.textMuted,
    fontSize: 12,
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  settingButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: AppColors.divider,
  },
  settingButtonText: {
    color: AppColors.textPrimary,
    fontSize: 16,
    fontWeight: "500",
  },
  chevron: {
    fontSize: 18,
    color: AppColors.textMuted,
  },
  aboutCard: {
    ...CommonStyles.card,
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
    marginBottom: 16,
  },
  aboutRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 12,
  },
  aboutLabel: {
    color: AppColors.textSecondary,
    fontSize: 14,
  },
  aboutValue: {
    color: AppColors.textPrimary,
    fontSize: 14,
    fontWeight: "600",
  },
  aboutLinks: {
    gap: 12,
  },
  aboutButton: {
    backgroundColor: AppColors.cardBackground,
    borderWidth: 1,
    borderColor: AppColors.border,
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
  },
  aboutButtonText: {
    fontSize: 14,
    fontWeight: "500",
    color: AppColors.primary,
  },
  dangerCard: {
    backgroundColor: AppColors.cardBackground,
    borderRadius: 16,
    overflow: "hidden",
    borderWidth: 2,
    borderColor: AppColors.error,
  },
  dangerButton: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: AppColors.error,
    alignItems: "center",
  },
  dangerButtonText: {
    fontSize: 14,
    fontWeight: "500",
    color: AppColors.error,
  },
});
