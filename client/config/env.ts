import Constants from "expo-constants";

interface Config {
  API_BASE_URL: string;
}

// Get API base URL from environment variable or use default
const getApiBaseUrl = (): string => {
  // Try process.env first (from .env file)
  if (process.env.EXPO_PUBLIC_API_BASE_URL) {
    return process.env.EXPO_PUBLIC_API_BASE_URL;
  }

  // Try Expo Constants as fallback
  if (Constants.expoConfig?.extra?.EXPO_PUBLIC_API_BASE_URL) {
    return Constants.expoConfig.extra.EXPO_PUBLIC_API_BASE_URL;
  }

  // Default fallback (your current IP)
  return "http://172.31.52.210:8000";
};

export const config: Config = {
  API_BASE_URL: getApiBaseUrl(),
};
