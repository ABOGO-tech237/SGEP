import path from "path";
import { fileURLToPath } from "url";
import type { NextConfig } from "next";

const frontendRoot = path.dirname(fileURLToPath(import.meta.url));

const nextConfig: NextConfig = {
  reactCompiler: true,
  // Évite que Turbopack prenne ~/package-lock.json comme racine du monorepo.
  turbopack: {
    root: frontendRoot,
  },
};

export default nextConfig;
