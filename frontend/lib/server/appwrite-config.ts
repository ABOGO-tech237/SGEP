const PLACEHOLDER_MARKERS = ["<", "YOUR"] as const;

export function isAppwriteEndpointValid(endpoint: string): boolean {
  if (!endpoint.trim()) return false;
  const upper = endpoint.toUpperCase();
  return !PLACEHOLDER_MARKERS.some(
    (marker) => endpoint.includes(marker) || upper.includes(marker),
  );
}

export interface AppwriteConfig {
  endpoint: string;
  projectId: string;
  apiKey: string;
}

export function getAppwriteConfig(): AppwriteConfig {
  const endpoint =
    process.env.APPWRITE_ENDPOINT ??
    process.env.NEXT_PUBLIC_APPWRITE_ENDPOINT ??
    "";
  const projectId =
    process.env.APPWRITE_PROJECT_ID ??
    process.env.NEXT_PUBLIC_APPWRITE_PROJECT_ID ??
    "";
  const apiKey = process.env.APPWRITE_API_KEY ?? "";

  return { endpoint, projectId, apiKey };
}

export function assertAppwriteConfig(): AppwriteConfig {
  const config = getAppwriteConfig();
  if (!isAppwriteEndpointValid(config.endpoint) || !config.projectId) {
    throw new Error("Appwrite is not configured");
  }
  return config;
}
