/** @type {import('next').NextConfig} */
const nextConfig = {
  allowedDevOrigins: ["10.0.0.102"],
  transpilePackages: ["@mediacreator/shared-types"]
};

export default nextConfig;
