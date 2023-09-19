import httpProxyMiddleware from 'next-http-proxy-middleware'

import {BackendUrl} from '../../config/vars.config'


export const config = {
  api: {
    bodyParser: false,
  },
}

export default function handler(req, res) {
  return httpProxyMiddleware(req, res, {
    target: BackendUrl,
  })
}
