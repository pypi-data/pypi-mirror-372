/** @type {import('next').NextConfig} */

const API_URL = "http://localhost:8004";

const nextConfig = {
  output: "export",
  experimental: {
    // serverActions: false,
  },
  webpack: (config) => {
    config.module.rules.push({
      test: /\.py$/,
      type: "asset/source",
    });
    config.module.rules.push({
      test: /\.ipynb$/,
      type: "asset/source",
    });
    config.module.rules.push({
      test: /\.html$/,
      type: "asset/source",
    });
    return config;
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${API_URL}/api/:path*`,
      },
      {
        source: "/_login",
        destination: `${API_URL}/_login`,
      },
      {
        source: "/_logout",
        destination: `${API_URL}/_logout`,
      },
    ];
  },
};

export default nextConfig;
