/**
 * Below are the colors that are used in the app. The colors are defined in the light and dark mode.
 * Enhanced for better contrast and accessibility.
 */

const tintColorLight = "#0066CC";
const tintColorDark = "#fff";

export const Colors = {
  light: {
    text: "#1A1A1A", // Darker text for better contrast
    background: "#FFFFFF",
    tint: tintColorLight,
    icon: "#4A5568", // Darker icons for better visibility
    tabIconDefault: "#4A5568",
    tabIconSelected: tintColorLight,
    // Additional colors for better contrast
    cardBackground: "#F7FAFC",
    border: "#E2E8F0",
    muted: "#64748B",
    success: "#059669",
    warning: "#D97706",
    error: "#DC2626",
  },
  dark: {
    text: "#FFFFFF",
    background: "#0F172A", // Darker background
    tint: tintColorDark,
    icon: "#CBD5E1",
    tabIconDefault: "#94A3B8",
    tabIconSelected: tintColorDark,
    // Additional colors for dark mode
    cardBackground: "#1E293B",
    border: "#334155",
    muted: "#94A3B8",
    success: "#10B981",
    warning: "#F59E0B",
    error: "#EF4444",
  },
};
