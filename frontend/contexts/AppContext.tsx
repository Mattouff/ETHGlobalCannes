import { APP_CONFIG } from "@/src/constants/config";
import { AIAgentService, TransactionService } from "@/src/services";
import { AppAction, AppState } from "@/src/types";
import React, {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useReducer,
} from "react";

const initialState: AppState = {
  walletConnected: false,
  walletAddress: null,
  connectedChain: null,
  agentStatus: {
    isActive: true,
    lastUpdate: Date.now(),
    marketDataSources: ["CoinGecko", "DeFiPulse", "CoinMarketCap"],
    newsSourcesActive: 5,
    confidenceLevel: 0.85,
  },
  intents: [
    {
      id: "1",
      type: "swap",
      fromToken: "ETH",
      toToken: "USDC",
      fromChain: "Ethereum",
      toChain: "Ethereum",
      amount: "0.5",
      estimatedGas: "0.002",
      confidence: 0.92,
      reasoning:
        "Market volatility indicators suggest ETH may decline 8-12% in next 24h. Converting to USDC recommended.",
      timestamp: Date.now() - 300000,
      status: "pending",
    },
    {
      id: "2",
      type: "bridge",
      fromToken: "USDC",
      toToken: "USDC",
      fromChain: "Ethereum",
      toChain: "Polygon",
      amount: "1000",
      estimatedGas: "0.015",
      confidence: 0.78,
      reasoning:
        "Lower transaction costs on Polygon for upcoming DeFi opportunities. Gas savings: ~85%.",
      timestamp: Date.now() - 600000,
      status: "pending",
    },
  ],
  assets: [
    {
      symbol: "ETH",
      name: "Ethereum",
      balance: "2.45",
      value: "$8,820.50",
      chain: "Ethereum",
    },
    {
      symbol: "USDC",
      name: "USD Coin",
      balance: "1,250.00",
      value: "$1,250.00",
      chain: "Ethereum",
      contractAddress: "0xa0b86a33e6728c9532b8e7c0b6b37e1235e26d1e",
    },
    {
      symbol: "MATIC",
      name: "Polygon",
      balance: "500.00",
      value: "$425.00",
      chain: "Polygon",
    },
  ],
  totalPortfolioValue: "$10,495.50",
  transactions: [
    {
      id: "1",
      hash: "0x1234...5678",
      type: "swap",
      fromToken: "USDC",
      toToken: "ETH",
      fromChain: "Ethereum",
      toChain: "Ethereum",
      amount: "1000",
      status: "confirmed",
      timestamp: Date.now() - 3600000,
      gasUsed: "0.0045",
    },
  ],
  loading: false,
  error: null,
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case "CONNECT_WALLET":
      return {
        ...state,
        walletConnected: true,
        walletAddress: action.payload.address,
        connectedChain: action.payload.chain,
      };

    case "DISCONNECT_WALLET":
      return {
        ...state,
        walletConnected: false,
        walletAddress: null,
        connectedChain: null,
      };

    case "SET_AGENT_STATUS":
      return {
        ...state,
        agentStatus: action.payload,
      };

    case "ADD_INTENT":
      return {
        ...state,
        intents: [action.payload, ...state.intents],
      };

    case "UPDATE_INTENT":
      return {
        ...state,
        intents: state.intents.map((intent) =>
          intent.id === action.payload.id
            ? { ...intent, status: action.payload.status }
            : intent
        ),
      };

    case "SET_ASSETS":
      return {
        ...state,
        assets: action.payload,
      };

    case "ADD_TRANSACTION":
      return {
        ...state,
        transactions: [action.payload, ...state.transactions],
      };

    case "UPDATE_TRANSACTION":
      return {
        ...state,
        transactions: state.transactions.map((tx) =>
          tx.id === action.payload.id
            ? {
                ...tx,
                status: action.payload.status,
                hash: action.payload.hash || tx.hash,
              }
            : tx
        ),
      };

    case "SET_LOADING":
      return {
        ...state,
        loading: action.payload,
      };

    case "SET_ERROR":
      return {
        ...state,
        error: action.payload,
      };

    default:
      return state;
  }
}

interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
  // Helper functions
  connectWallet: (address: string, chain: string) => void;
  disconnectWallet: () => void;
  approveIntent: (intentId: string) => void;
  rejectIntent: (intentId: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Helper functions
  const connectWallet = (address: string, chain: string) => {
    dispatch({ type: "CONNECT_WALLET", payload: { address, chain } });
  };

  const disconnectWallet = () => {
    dispatch({ type: "DISCONNECT_WALLET" });
  };

  const approveIntent = (intentId: string) => {
    dispatch({
      type: "UPDATE_INTENT",
      payload: { id: intentId, status: "approved" },
    });

    // Simulate transaction creation
    const intent = state.intents.find((i) => i.id === intentId);
    if (intent) {
      const transaction =
        TransactionService.createTransactionFromIntent(intent);
      dispatch({ type: "ADD_TRANSACTION", payload: transaction });

      // Simulate transaction confirmation
      setTimeout(() => {
        dispatch({
          type: "UPDATE_TRANSACTION",
          payload: { id: transaction.id, status: "confirmed" },
        });
        dispatch({
          type: "UPDATE_INTENT",
          payload: { id: intentId, status: "executed" },
        });
      }, APP_CONFIG.TRANSACTION_CONFIRMATION_DELAY);
    }
  };

  const rejectIntent = (intentId: string) => {
    dispatch({
      type: "UPDATE_INTENT",
      payload: { id: intentId, status: "rejected" },
    });
  };

  // Simulate new intents from AI agent
  useEffect(() => {
    const interval = setInterval(() => {
      if (Math.random() > 0.7) {
        // 30% chance
        const newIntent = AIAgentService.generateIntent();
        dispatch({ type: "ADD_INTENT", payload: newIntent });
      }
    }, APP_CONFIG.INTENT_GENERATION_INTERVAL);

    return () => clearInterval(interval);
  }, []);

  const value: AppContextType = {
    state,
    dispatch,
    connectWallet,
    disconnectWallet,
    approveIntent,
    rejectIntent,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
}
