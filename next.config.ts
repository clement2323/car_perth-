import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // En dev : proxy /api/* vers uvicorn sur :8000
  // En prod (Vercel) : les requêtes /api/* sont interceptées par api/index.py
  //                    via les rewrites de vercel.json (pas besoin de proxy)
  async rewrites() {
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/:path*',
          destination: 'http://localhost:8000/api/:path*',
        },
      ]
    }
    return []
  },
}

export default nextConfig
