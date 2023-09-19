import {register, collectDefaultMetrics} from 'prom-client'

collectDefaultMetrics({})

export default async function handler(_, res) {
  res.setHeader('Content-type', register.contentType)
  res.send(await register.metrics())
};
