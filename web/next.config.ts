import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // output: 'export',  // Disabled for development - enable when needed for static export
  images: {
    unoptimized: true,
  },
  // trailingSlash: true,  // Only needed for static export
};

export default nextConfig;
