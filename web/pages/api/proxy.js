import httpProxyMiddleware from 'next-http-proxy-middleware'

export default async function handler(req, res) {
  const {url} = req.query
  return httpProxyMiddleware(req, res, {
    target: url,
    ignorePath: true,
  })
}
