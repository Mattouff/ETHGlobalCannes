// App configuration constants
export const APP_CONFIG = {
  APP_NAME: "AI Agent Cross-Chain Portfolio",
  VERSION: "1.0.0",
  API_TIMEOUT: 10000,
  INTENT_GENERATION_INTERVAL: 30000, // 30 seconds
  TRANSACTION_CONFIRMATION_DELAY: 3000, // 3 seconds
} as const;

// Supported chains
export const SUPPORTED_CHAINS = {
  ETHEREUM: "Ethereum",
  POLYGON: "Polygon",
  ARBITRUM: "Arbitrum",
  OPTIMISM: "Optimism",
} as const;

// Transaction types
export const TRANSACTION_TYPES = {
  SWAP: "swap",
  BRIDGE: "bridge",
  STAKE: "stake",
} as const;

// Status values
export const INTENT_STATUS = {
  PENDING: "pending",
  APPROVED: "approved",
  REJECTED: "rejected",
  EXECUTED: "executed",
} as const;

export const TRANSACTION_STATUS = {
  PENDING: "pending",
  CONFIRMED: "confirmed",
  FAILED: "failed",
} as const;

// Animation durations
export const ANIMATION_DURATION = {
  SHORT: 200,
  MEDIUM: 300,
  LONG: 500,
} as const;

// Common spacing values
export const SPACING = {
  XS: 4,
  SM: 8,
  MD: 12,
  LG: 16,
  XL: 20,
  XXL: 24,
  XXXL: 32,
} as const;

// Font sizes
export const FONT_SIZE = {
  XS: 10,
  SM: 12,
  MD: 14,
  LG: 16,
  XL: 18,
  XXL: 20,
  XXXL: 24,
  TITLE: 28,
  LARGE_TITLE: 32,
} as const;
