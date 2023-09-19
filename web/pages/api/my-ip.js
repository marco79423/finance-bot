import geoip from 'geoip-lite'

export default async function handler(req, res) {
  const forwarded = req.headers['x-forwarded-for']
  const ip = forwarded ? forwarded.split(/, /)[0] : req.connection.remoteAddress

  const geo = geoip.lookup(ip)

  res.status(200).json({
    data: {
      ip,
      geo,
    }
  })
};
