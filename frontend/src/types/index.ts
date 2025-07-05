// Core application types
export interface Intent {
  id: string;
  type: "swap" | "bridge" | "stake";
  fromToken: string;
  toToken: string;
  fromChain: string;
  toChain: string;
  amount: string;
  estimatedGas: string;
  confidence: number;
  reasoning: string;
  timestamp: number;
  status: "pending" | "approved" | "rejected" | "executed";
}

export interface Transaction {
  id: string;
  hash: string;
  type: "swap" | "bridge" | "stake";
  fromToken: string;
  toToken: string;
  fromChain: string;
  toChain: string;
  amount: string;
  status: "pending" | "confirmed" | "failed";
  timestamp: number;
  gasUsed?: string;
}

export interface Asset {
  symbol: string;
  name: string;
  balance: string;
  value: string;
  chain: string;
  contractAddress?: string;
}

export interface AgentStatus {
  isActive: boolean;
  lastUpdate: number;
  marketDataSources: string[];
  newsSourcesActive: number;
  confidenceLevel: number;
}

// App State interface
export interface AppState {
  // Wallet
  walletConnected: boolean;
  walletAddress: string | null;
  connectedChain: string | null;

  // Agent
  agentStatus: AgentStatus;
  intents: Intent[];

  // Portfolio
  assets: Asset[];
  totalPortfolioValue: string;

  // Transactions
  transactions: Transaction[];

  // UI
  loading: boolean;
  error: string | null;
}

// Action types
export type AppAction =
  | { type: "CONNECT_WALLET"; payload: { address: string; chain: string } }
  | { type: "DISCONNECT_WALLET" }
  | { type: "SET_AGENT_STATUS"; payload: AgentStatus }
  | { type: "ADD_INTENT"; payload: Intent }
  | { type: "UPDATE_INTENT"; payload: { id: string; status: Intent["status"] } }
  | { type: "SET_ASSETS"; payload: Asset[] }
  | { type: "ADD_TRANSACTION"; payload: Transaction }
  | {
      type: "UPDATE_TRANSACTION";
      payload: { id: string; status: Transaction["status"]; hash?: string };
    }
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "SET_ERROR"; payload: string | null };

// Wallet types
export interface WalletState {
  isConnected: boolean;
  address: string | null;
  isConnecting: boolean;
  error: string | null;
}

export type WalletAction =
  | { type: "CONNECTING" }
  | { type: "CONNECTED"; payload: string }
  | { type: "DISCONNECTED" }
  | { type: "ERROR"; payload: string };
