/**
 * Exemple d'intégration CCIP pour React Native
 * Utilise l'API IntentFi CCIP pour les transferts cross-chain
 */

import { useState, useEffect } from 'react';

// Configuration API
const API_BASE_URL = 'http://localhost:5001'; // À remplacer par votre URL de production

// Types TypeScript
interface CCIPChain {
  name: string;
  chain_id: number;
  selector: string;
  native_symbol: string;
  router: string;
  link_token: string;
}

interface CCIPTransfer {
  id: string;
  source_chain: string;
  destination_chain: string;
  sender: string;
  receiver: string;
  amount: number;
  token_address?: string;
  status: string;
  created_at: string;
}

interface Intent {
  id: string;
  owner: string;
  intent_type: string;
  trigger_price: number;
  amount: number;
  source_chain: string;
  destination_chain: string;
  receiver: string;
  status: string;
  created_at: string;
}

// Hook pour CCIP
export const useCCIP = () => {
  const [chains, setChains] = useState<CCIPChain[]>([]);
  const [transfers, setTransfers] = useState<CCIPTransfer[]>([]);
  const [loading, setLoading] = useState(false);

  // Récupérer les chaînes supportées
  const fetchSupportedChains = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/ccip/chains`);
      const data = await response.json();
      if (data.success) {
        setChains(data.chains);
      }
    } catch (error) {
      console.error('Error fetching chains:', error);
    }
  };

  // Calculer les frais CCIP
  const calculateFees = async (
    sourceChain: string,
    destChain: string,
    amount: number,
    tokenAddress?: string,
    receiver?: string
  ) => {
    try {
      const response = await fetch(`${API_BASE_URL}/ccip/fees/${sourceChain}/${destChain}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount,
          token_address: tokenAddress,
          receiver: receiver || '0x0000000000000000000000000000000000000000'
        })
      });
      const data = await response.json();
      return data.success ? data.fees : null;
    } catch (error) {
      console.error('Error calculating fees:', error);
      return null;
    }
  };

  // Initier un transfert CCIP
  const initiateCCIPTransfer = async (
    sourceChain: string,
    destChain: string,
    amount: number,
    receiver: string,
    sender: string,
    tokenAddress?: string
  ) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/ccip/transfer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_chain: sourceChain,
          destination_chain: destChain,
          amount,
          token_address: tokenAddress,
          receiver,
          sender
        })
      });
      const data = await response.json();
      return data.success ? data : null;
    } catch (error) {
      console.error('Error initiating transfer:', error);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Vérifier le statut d'un transfert
  const getTransferStatus = async (txId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/ccip/status/${txId}`);
      const data = await response.json();
      return data.success ? data.transaction : null;
    } catch (error) {
      console.error('Error getting transfer status:', error);
      return null;
    }
  };

  // Récupérer l'historique des transferts
  const fetchTransferHistory = async (address: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/ccip/history/${address}`);
      const data = await response.json();
      if (data.success) {
        setTransfers(data.transactions);
      }
    } catch (error) {
      console.error('Error fetching transfer history:', error);
    }
  };

  useEffect(() => {
    fetchSupportedChains();
  }, []);

  return {
    chains,
    transfers,
    loading,
    calculateFees,
    initiateCCIPTransfer,
    getTransferStatus,
    fetchTransferHistory
  };
};

// Hook pour les Intents
export const useIntents = () => {
  const [intents, setIntents] = useState<Intent[]>([]);
  const [loading, setLoading] = useState(false);

  // Créer un intent
  const createIntent = async (
    owner: string,
    intentType: string,
    triggerPrice: number,
    amount: number,
    sourceChain: string,
    destChain: string,
    receiver: string,
    tokenAddress?: string
  ) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/intent/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          owner,
          intent_type: intentType,
          trigger_price: triggerPrice,
          amount,
          token_address: tokenAddress,
          source_chain: sourceChain,
          destination_chain: destChain,
          receiver
        })
      });
      const data = await response.json();
      return data.success ? data : null;
    } catch (error) {
      console.error('Error creating intent:', error);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Récupérer les intents d'un utilisateur
  const fetchUserIntents = async (address: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/intent/list/${address}`);
      const data = await response.json();
      if (data.success) {
        setIntents(data.intents);
      }
    } catch (error) {
      console.error('Error fetching intents:', error);
    }
  };

  // Exécuter un intent
  const executeIntent = async (intentId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/intent/execute/${intentId}`, {
        method: 'POST'
      });
      const data = await response.json();
      return data.success ? data : null;
    } catch (error) {
      console.error('Error executing intent:', error);
      return null;
    }
  };

  // Annuler un intent
  const cancelIntent = async (intentId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/intent/cancel/${intentId}`, {
        method: 'POST'
      });
      const data = await response.json();
      return data.success ? data : null;
    } catch (error) {
      console.error('Error cancelling intent:', error);
      return null;
    }
  };

  return {
    intents,
    loading,
    createIntent,
    fetchUserIntents,
    executeIntent,
    cancelIntent
  };
};

// Composant d'exemple pour les transferts CCIP
export const CCIPTransferComponent = () => {
  const { chains, calculateFees, initiateCCIPTransfer } = useCCIP();
  const [selectedSourceChain, setSelectedSourceChain] = useState('');
  const [selectedDestChain, setSelectedDestChain] = useState('');
  const [amount, setAmount] = useState('');
  const [receiver, setReceiver] = useState('');
  const [fees, setFees] = useState(null);

  const handleCalculateFees = async () => {
    if (selectedSourceChain && selectedDestChain && amount) {
      const feeData = await calculateFees(
        selectedSourceChain,
        selectedDestChain,
        parseFloat(amount),
        undefined,
        receiver
      );
      setFees(feeData);
    }
  };

  const handleTransfer = async () => {
    // Cette fonction nécessiterait l'intégration avec le wallet de l'utilisateur
    // pour obtenir l'adresse sender et signer la transaction
    console.log('Transfer initiated...');
  };

  return {
    chains,
    selectedSourceChain,
    setSelectedSourceChain,
    selectedDestChain,
    setSelectedDestChain,
    amount,
    setAmount,
    receiver,
    setReceiver,
    fees,
    handleCalculateFees,
    handleTransfer
  };
};

// Composant d'exemple pour les intents
export const IntentManagerComponent = () => {
  const { intents, createIntent, fetchUserIntents, executeIntent, cancelIntent } = useIntents();
  const [userAddress, setUserAddress] = useState('');
  
  const handleCreateIntent = async (
    intentType: string,
    triggerPrice: number,
    amount: number,
    sourceChain: string,
    destChain: string,
    receiver: string
  ) => {
    if (userAddress) {
      const result = await createIntent(
        userAddress,
        intentType,
        triggerPrice,
        amount,
        sourceChain,
        destChain,
        receiver
      );
      
      if (result) {
        // Recharger les intents
        await fetchUserIntents(userAddress);
      }
    }
  };

  return {
    intents,
    userAddress,
    setUserAddress,
    handleCreateIntent,
    fetchUserIntents,
    executeIntent,
    cancelIntent
  };
};

// Utilitaires
export const CCIPUtils = {
  // Formater les montants
  formatAmount: (amount: number, decimals: number = 4) => {
    return amount.toFixed(decimals);
  },

  // Formater les adresses
  formatAddress: (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  },

  // Estimer le temps de transfert
  estimateTransferTime: async (sourceChain: string, destChain: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/ccip/estimate-time/${sourceChain}/${destChain}`);
      const data = await response.json();
      return data.success ? data.estimated_time_human : null;
    } catch (error) {
      console.error('Error estimating transfer time:', error);
      return null;
    }
  },

  // Vérifier la santé du système
  checkSystemHealth: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/ccip/health`);
      const data = await response.json();
      return data.success ? data.health : null;
    } catch (error) {
      console.error('Error checking system health:', error);
      return null;
    }
  }
};

export default {
  useCCIP,
  useIntents,
  CCIPTransferComponent,
  IntentManagerComponent,
  CCIPUtils
};
