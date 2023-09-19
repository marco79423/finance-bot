export default function detectMobileByReq(req) {
  const UA = req.headers['user-agent']
  return Boolean(UA?.match(
    /Android|BlackBerry|iPhone|iPad|iPod|Opera Mini|IEMobile|WPDesktop/i
  ))
}
