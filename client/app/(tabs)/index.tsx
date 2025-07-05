import {
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  Dimensions,
} from "react-native";
import { useAppKit, AppKitButton } from "@reown/appkit-wagmi-react-native";
import { useAccount } from "wagmi";

import { ThemedText } from "@/components/ThemedText";
import { ThemedView } from "@/components/ThemedView";

const { width } = Dimensions.get("window");

export default function HomeScreen() {
  const { open } = useAppKit();
  const { isConnected } = useAccount();

  if (!isConnected) {
    return (
      <SafeAreaView style={styles.container}>
        <ThemedView style={styles.landingContainer}>
          <ScrollView
            contentContainerStyle={styles.scrollContainer}
            showsVerticalScrollIndicator={false}
          >
            <ThemedView style={styles.headerSection}>
              <ThemedView style={styles.logoContainer}>
                <ThemedText style={styles.logoText}>⚡</ThemedText>
              </ThemedView>

              <ThemedText style={styles.title}>IntentFi</ThemedText>

              <ThemedText style={styles.tagline}>
                Smart Autonomous Scheduling for Financial Intents
              </ThemedText>
            </ThemedView>

            <ThemedView style={styles.descriptionSection}>
              <ThemedText style={styles.description}>
                We are building IntentFi, a revolutionary platform that
                automates and optimizes your financial operations through
                intelligent intent scheduling.
              </ThemedText>

              <ThemedView style={styles.featuresGrid}>
                <ThemedView style={styles.featureCard}>
                  <ThemedText style={styles.featureIcon}>🤖</ThemedText>
                  <ThemedText style={styles.featureTitle}>
                    Autonomous
                  </ThemedText>
                  <ThemedText style={styles.featureDesc}>
                    AI-powered decision making
                  </ThemedText>
                </ThemedView>

                <ThemedView style={styles.featureCard}>
                  <ThemedText style={styles.featureIcon}>⚡</ThemedText>
                  <ThemedText style={styles.featureTitle}>Smart</ThemedText>
                  <ThemedText style={styles.featureDesc}>
                    Optimized execution
                  </ThemedText>
                </ThemedView>

                <ThemedView style={styles.featureCard}>
                  <ThemedText style={styles.featureIcon}>🎯</ThemedText>
                  <ThemedText style={styles.featureTitle}>
                    Intent-Based
                  </ThemedText>
                  <ThemedText style={styles.featureDesc}>
                    Focus on outcomes
                  </ThemedText>
                </ThemedView>

                <ThemedView style={styles.featureCard}>
                  <ThemedText style={styles.featureIcon}>🔒</ThemedText>
                  <ThemedText style={styles.featureTitle}>Secure</ThemedText>
                  <ThemedText style={styles.featureDesc}>
                    Enterprise-grade security
                  </ThemedText>
                </ThemedView>
              </ThemedView>
            </ThemedView>

            <ThemedView style={styles.ctaSection}>
              <TouchableOpacity
                style={styles.connectButton}
                onPress={() => open()}
              >
                <ThemedView style={styles.buttonContainer}>
                  <ThemedText style={styles.connectButtonText}>
                    Connect Wallet & Start
                  </ThemedText>
                </ThemedView>
              </TouchableOpacity>

              <ThemedText style={styles.supportText}>
                Supported on Ethereum, Polygon & Arbitrum
              </ThemedText>
            </ThemedView>
          </ScrollView>
        </ThemedView>
      </SafeAreaView>
    );
  }

  // Dashboard connecté
  return (
    <SafeAreaView style={styles.container}>
      <ThemedView style={styles.dashboardContainer}>
        <ScrollView
          contentContainerStyle={styles.dashboardContent}
          showsVerticalScrollIndicator={false}
        >
          <ThemedView style={styles.dashboardHeader}>
            <ThemedText style={styles.welcomeTitle}>
              Welcome to IntentFi 🎯
            </ThemedText>

            <ThemedView style={styles.walletSection}>
              <ThemedText style={styles.walletLabel}>Your Wallet</ThemedText>
              <ThemedView style={styles.walletButtonContainer}>
                <AppKitButton />
              </ThemedView>
            </ThemedView>
          </ThemedView>

          <ThemedView style={styles.statsSection}>
            <ThemedText style={styles.sectionTitle}>
              Dashboard Overview
            </ThemedText>

            <ThemedView style={styles.statsGrid}>
              <ThemedView style={styles.statCard}>
                <ThemedText style={styles.statIcon}>💰</ThemedText>
                <ThemedText style={styles.statValue}>$2,456.78</ThemedText>
                <ThemedText style={styles.statLabel}>
                  Total Portfolio
                </ThemedText>
              </ThemedView>

              <ThemedView style={styles.statCard}>
                <ThemedText style={styles.statIcon}>🎯</ThemedText>
                <ThemedText style={styles.statValue}>3</ThemedText>
                <ThemedText style={styles.statLabel}>Active Intents</ThemedText>
              </ThemedView>

              <ThemedView style={styles.statCard}>
                <ThemedText style={styles.statIcon}>⚡</ThemedText>
                <ThemedText style={styles.statValue}>7</ThemedText>
                <ThemedText style={styles.statLabel}>Executed Today</ThemedText>
              </ThemedView>

              <ThemedView style={styles.statCard}>
                <ThemedText style={styles.statIcon}>📈</ThemedText>
                <ThemedText style={styles.statValue}>94%</ThemedText>
                <ThemedText style={styles.statLabel}>Success Rate</ThemedText>
              </ThemedView>
            </ThemedView>
          </ThemedView>

          <ThemedView style={styles.tokensSection}>
            <ThemedText style={styles.sectionTitle}>Your Tokens</ThemedText>

            <ThemedView style={styles.tokensList}>
              <ThemedView style={styles.tokenCard}>
                <ThemedView style={styles.tokenHeader}>
                  <ThemedText style={styles.tokenSymbol}>ETH</ThemedText>
                  <ThemedText style={styles.tokenValue}>$1,234.56</ThemedText>
                </ThemedView>
                <ThemedView style={styles.tokenDetails}>
                  <ThemedText style={styles.tokenAmount}>0.5 ETH</ThemedText>
                  <ThemedText style={styles.tokenPrice}>$2,469.12</ThemedText>
                </ThemedView>
              </ThemedView>

              <ThemedView style={styles.tokenCard}>
                <ThemedView style={styles.tokenHeader}>
                  <ThemedText style={styles.tokenSymbol}>USDC</ThemedText>
                  <ThemedText style={styles.tokenValue}>$856.00</ThemedText>
                </ThemedView>
                <ThemedView style={styles.tokenDetails}>
                  <ThemedText style={styles.tokenAmount}>856 USDC</ThemedText>
                  <ThemedText style={styles.tokenPrice}>$1.00</ThemedText>
                </ThemedView>
              </ThemedView>

              <ThemedView style={styles.tokenCard}>
                <ThemedView style={styles.tokenHeader}>
                  <ThemedText style={styles.tokenSymbol}>MATIC</ThemedText>
                  <ThemedText style={styles.tokenValue}>$366.22</ThemedText>
                </ThemedView>
                <ThemedView style={styles.tokenDetails}>
                  <ThemedText style={styles.tokenAmount}>420 MATIC</ThemedText>
                  <ThemedText style={styles.tokenPrice}>$0.87</ThemedText>
                </ThemedView>
              </ThemedView>
            </ThemedView>
          </ThemedView>
        </ScrollView>
      </ThemedView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0)",
  },

  // Landing Page Styles
  landingContainer: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0)",
  },
  scrollContainer: {
    flexGrow: 1,
    paddingHorizontal: 20,
    paddingTop: 100, // Encore plus d'espace pour éviter la troncature
    paddingBottom: 40,
    backgroundColor: "rgba(0, 0, 0, 0)",
  },
  headerSection: {
    alignItems: "center",
    marginBottom: 50,
    backgroundColor: "rgba(0, 0, 0, 0)",
  },
  logoContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: "rgba(0, 0, 0, 0)",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 24,
  },
  logoText: {
    fontSize: 40,
    color: "#fff",
  },
  title: {
    fontSize: 42, // Réduit légèrement
    fontWeight: "bold",
    color: "#fff",
    textAlign: "center",
    marginBottom: 16,
    letterSpacing: -1,
  },
  tagline: {
    fontSize: 18,
    color: "rgba(255, 255, 255, 0.8)",
    textAlign: "center",
    lineHeight: 26,
    paddingHorizontal: 20,
  },
  descriptionSection: {
    marginBottom: 50,
    backgroundColor: "rgba(0, 0, 0, 0)",
  },
  description: {
    fontSize: 16,
    color: "rgba(255, 255, 255, 0.7)",
    textAlign: "center",
    lineHeight: 24,
    marginBottom: 40,
    paddingHorizontal: 10,
    backgroundColor: "rgba(0, 0, 0, 0)",
  },
  featuresGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    backgroundColor: "rgba(0, 0, 0, 0)",
    gap: 16,
  },
  featureCard: {
    width: (width - 56) / 2,
    borderRadius: 16,
    padding: 20,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "rgba(255, 255, 255, 0.1)",
    backgroundColor: "rgba(0, 0, 0, 0)",
  },
  featureIcon: {
    fontSize: 32,
    marginBottom: 12,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: "bold",
    paddingTop: 4,
    color: "#fff",
    marginBottom: 8,
    textAlign: "center",
  },
  featureDesc: {
    fontSize: 12,
    color: "rgba(255, 255, 255, 0.7)",
    textAlign: "center",
    lineHeight: 16,
  },
  ctaSection: {
    alignItems: "center",
    marginTop: 40,
    backgroundColor: "rgba(0, 0, 0, 0)",
  },
  connectButton: {
    borderRadius: 50,
    marginBottom: 20,
    backgroundColor: "#6366f1",
    elevation: 8,
    shadowColor: "#6366f1",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  buttonContainer: {
    paddingVertical: 18,
    paddingHorizontal: 40,
    borderRadius: 50,
    minWidth: 280,
    alignItems: "center",
    backgroundColor: "rgba(0, 0, 0, 0)",
  },
  connectButtonText: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "bold",
  },
  supportText: {
    fontSize: 14,
    color: "rgba(255, 255, 255, 0.6)",
    textAlign: "center",
  },

  // Dashboard Styles
  dashboardContainer: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0)",
  },
  dashboardContent: {
    flexGrow: 1,
    paddingHorizontal: 20,
    paddingTop: 100, // Plus d'espace pour éviter le texte tronqué
    paddingBottom: 40,
    backgroundColor: "rgba(0, 0, 0, 0)",
  },
  dashboardHeader: {
    backgroundColor: "rgba(0, 0, 0, 0)",
    alignItems: "center",
    marginBottom: 40,
  },
  welcomeTitle: {
    fontSize: 24, // Réduit pour éviter la troncature
    fontWeight: "bold",
    color: "#fff",
    textAlign: "center",
    marginBottom: 24,
    paddingHorizontal: 10,
  },
  walletSection: {
    marginBottom: 20,
    alignItems: "center",
    backgroundColor: "rgba(0, 0, 0, 0)",
  },
  walletLabel: {
    fontSize: 16,
    fontWeight: "600",
    color: "rgba(255, 255, 255, 0.8)",
    marginBottom: 12,
    textAlign: "center",
  },
  walletButtonContainer: {
    backgroundColor: "rgba(255, 255, 255, 0.05)",
    borderRadius: 12,
    padding: 8,
    borderWidth: 1,
    borderColor: "rgba(255, 255, 255, 0.1)",
  },
  statsSection: {
    marginBottom: 40,
    backgroundColor: "rgba(0, 0, 0, 0)",
  },
  sectionTitle: {
    fontSize: 22, // Réduit pour éviter la troncature
    fontWeight: "bold",
    color: "#fff",
    marginBottom: 20,
    textAlign: "center",
    paddingHorizontal: 10,
  },
  statsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    gap: 16,
    backgroundColor: "rgba(0, 0, 0, 0)",
  },
  statCard: {
    width: (width - 56) / 2,
    borderRadius: 20,
    padding: 20, // Réduit pour plus d'espace
    alignItems: "center",
    borderWidth: 1,
    borderColor: "rgba(255, 255, 255, 0.1)",
  },
  statIcon: {
    fontSize: 28, // Réduit
    marginBottom: 8,
  },
  statValue: {
    fontSize: 24, // Réduit
    fontWeight: "bold",
    color: "#fff",
    marginBottom: 6,
  },
  statLabel: {
    fontSize: 12, // Réduit
    color: "rgba(255, 255, 255, 0.7)",
    textAlign: "center",
  },

  // Tokens Section
  tokensSection: {
    marginTop: 20,
    backgroundColor: "rgba(0, 0, 0, 0)",
    marginBottom: 60,
  },
  tokensList: {
    gap: 12,
    backgroundColor: "rgba(0, 0, 0, 0)",
  },
  tokenCard: {
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: "rgba(255, 255, 255, 0.1)",
  },
  tokenHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  tokenSymbol: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#fff",
  },
  tokenValue: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#4ade80",
  },
  tokenDetails: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  tokenAmount: {
    fontSize: 14,
    color: "rgba(255, 255, 255, 0.7)",
  },
  tokenPrice: {
    fontSize: 14,
    color: "rgba(255, 255, 255, 0.5)",
  },
});
