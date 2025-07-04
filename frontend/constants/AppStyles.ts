import { StyleSheet } from "react-native";

// Common colors with proper contrast ratios
export const AppColors = {
  // Backgrounds
  cardBackground: "#FFFFFF",
  screenBackground: "#F8FAFC",
  modalBackground: "rgba(0, 0, 0, 0.5)",

  // Text colors with proper contrast
  textPrimary: "#1A202C", // Very dark for high contrast
  textSecondary: "#4A5568", // Medium dark for secondary text
  textMuted: "#718096", // For less important text
  textInverse: "#FFFFFF", // White text on dark backgrounds

  // Accent colors with sufficient contrast
  primary: "#0066CC", // Blue with good contrast
  success: "#059669", // Green with proper contrast
  warning: "#D97706", // Orange with good visibility
  error: "#DC2626", // Red with high contrast

  // Semantic colors
  intentPending: "#F59E0B",
  intentApproved: "#059669",
  intentRejected: "#DC2626",
  intentExecuted: "#8B5CF6",

  // Border and divider colors
  border: "#E2E8F0",
  divider: "#CBD5E0",

  // Status indicators
  online: "#10B981",
  offline: "#EF4444",

  // Chart and graph colors
  chart1: "#0066CC",
  chart2: "#059669",
  chart3: "#D97706",
  chart4: "#8B5CF6",
};

// Common styles with improved contrast
export const CommonStyles = StyleSheet.create({
  // Card styles with better contrast
  card: {
    backgroundColor: AppColors.cardBackground,
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },

  // Text styles with proper contrast
  textPrimary: {
    color: AppColors.textPrimary,
    fontSize: 16,
    fontWeight: "500",
  },

  textSecondary: {
    color: AppColors.textSecondary,
    fontSize: 14,
  },

  textMuted: {
    color: AppColors.textMuted,
    fontSize: 12,
  },

  textBold: {
    color: AppColors.textPrimary,
    fontSize: 16,
    fontWeight: "600",
  },

  // Button styles with proper contrast
  primaryButton: {
    backgroundColor: AppColors.primary,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: "center",
  },

  primaryButtonText: {
    color: AppColors.textInverse,
    fontSize: 16,
    fontWeight: "600",
  },

  secondaryButton: {
    backgroundColor: "transparent",
    borderWidth: 2,
    borderColor: AppColors.primary,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: "center",
  },

  secondaryButtonText: {
    color: AppColors.primary,
    fontSize: 16,
    fontWeight: "600",
  },

  // Status badges with high contrast
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },

  statusBadgeText: {
    color: AppColors.textInverse,
    fontSize: 12,
    fontWeight: "600",
  },

  // Input styles
  input: {
    borderWidth: 1,
    borderColor: AppColors.border,
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: AppColors.textPrimary,
    backgroundColor: AppColors.cardBackground,
  },

  // Section styles
  section: {
    padding: 24,
    paddingTop: 0,
  },

  sectionTitle: {
    color: AppColors.textPrimary,
    fontSize: 20,
    fontWeight: "600",
    marginBottom: 16,
  },

  // Header styles
  header: {
    padding: 24,
    paddingTop: 60,
  },

  headerTitle: {
    color: AppColors.textPrimary,
    fontSize: 28,
    fontWeight: "700",
  },

  headerSubtitle: {
    color: AppColors.textSecondary,
    fontSize: 16,
    marginTop: 8,
  },
});
