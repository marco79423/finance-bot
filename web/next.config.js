const {i18n} = require('./next-i18next.config')

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Docker 打包用
  output: 'standalone',

  compiler: {
    emotion: true
  },

  reactStrictMode: true,

  i18n,
}

module.exports = nextConfig
