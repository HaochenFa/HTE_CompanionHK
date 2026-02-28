const RAW_API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

function trimTrailingSlash(url: string): string {
  return url.endsWith("/") ? url.slice(0, -1) : url;
}

export function apiBaseUrl(): string {
  const normalized = trimTrailingSlash(RAW_API_BASE_URL);
  return normalized.endsWith("/api") ? normalized : `${normalized}/api`;
}
