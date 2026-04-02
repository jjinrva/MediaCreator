const INTERNAL_DEFAULT_API_BASE_URL = "http://127.0.0.1:8010";

function getExplicitPublicApiBase(): string | null {
  const publicApiBase = process.env.NEXT_PUBLIC_MEDIACREATOR_API_BASE_URL?.trim();
  return publicApiBase ? publicApiBase : null;
}

export function getApiBase(): string {
  const explicitPublicApiBase = getExplicitPublicApiBase();
  if (explicitPublicApiBase) {
    return explicitPublicApiBase;
  }

  if (typeof window !== "undefined") {
    return `${window.location.protocol}//${window.location.hostname}:8010`;
  }

  const internalApiBase = process.env.MEDIACREATOR_INTERNAL_API_BASE_URL?.trim();
  return internalApiBase || INTERNAL_DEFAULT_API_BASE_URL;
}
