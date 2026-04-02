function normalizeAllowedDevOrigin(origin) {
  const trimmedOrigin = origin.trim();
  if (!trimmedOrigin) {
    return null;
  }

  try {
    return new URL(trimmedOrigin).hostname;
  } catch {
    return trimmedOrigin;
  }
}

const allowedDevOrigins = (process.env.MEDIACREATOR_ALLOWED_DEV_ORIGINS ?? "")
  .split(",")
  .map((origin) => normalizeAllowedDevOrigin(origin))
  .filter(Boolean);

/** @type {import('next').NextConfig} */
const nextConfig = {
  ...(allowedDevOrigins.length > 0 ? { allowedDevOrigins } : {}),
  transpilePackages: ["@mediacreator/shared-types"]
};

export default nextConfig;
