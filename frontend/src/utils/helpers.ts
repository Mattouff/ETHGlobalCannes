/**
 * Format wallet address to show first 6 and last 4 characters
 */
export const formatAddress = (address: string): string => {
  if (!address) return "";
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
};

/**
 * Format timestamp to human readable time ago
 */
export const formatTimeAgo = (timestamp: number): string => {
  const minutes = Math.floor((Date.now() - timestamp) / 60000);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
};

/**
 * Generate random transaction hash for demo purposes
 */
export const generateTxHash = (): string => {
  return `0x${Math.random().toString(16).substr(2, 8)}...${Math.random()
    .toString(16)
    .substr(2, 8)}`;
};

/**
 * Get status color based on status type
 */
export const getStatusColor = (status: string): string => {
  switch (status) {
    case "pending":
      return "#F59E0B";
    case "approved":
    case "confirmed":
      return "#10B981";
    case "rejected":
    case "failed":
      return "#EF4444";
    case "executed":
      return "#8B5CF6";
    default:
      return "#6B7280";
  }
};

/**
 * Get icon for transaction/intent type
 */
export const getTypeIcon = (type: string): string => {
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

/**
 * Get chain icon
 */
export const getChainIcon = (chain: string): string => {
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

/**
 * Format large numbers with proper abbreviations
 */
export const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + "M";
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + "K";
  }
  return num.toString();
};

/**
 * Validate Ethereum address
 */
export const isValidEthereumAddress = (address: string): boolean => {
  return /^0x[a-fA-F0-9]{40}$/.test(address);
};
