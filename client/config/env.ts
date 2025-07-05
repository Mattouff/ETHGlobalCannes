import Constants from "expo-constants";

interface Config {
  API_BASE_AGENT_URL: string;
  API_BASE_API_URL: string;
}

export const config: Config = {
  API_BASE_AGENT_URL: process.env.EXPO_PUBLIC_API_BASE_AGENT_URL!,
  API_BASE_API_URL: process.env.EXPO_PUBLIC_API_BASE_API_URL!,
};
