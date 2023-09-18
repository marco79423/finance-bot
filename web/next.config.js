/** @type {import('next').NextConfig} */
const nextConfig = {
  // Docker 打包用
  output: 'standalone',

  compiler: {
    emotion: true
  },

  reactStrictMode: true,
}

module.exports = nextConfig
