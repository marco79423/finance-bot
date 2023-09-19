import {useRouter} from 'next/router'

/**
 * 取得網頁 Canonical URL
 * @returns {string} canonicalURL - 網頁的 Canonical URL
 */
export default function useCanonicalUrl(hostUrl) {
  const router = useRouter()

  const pathEnd = Math.min.apply(Math, [
    router.asPath.indexOf('?') > 0 ? router.asPath.indexOf('?') : router.asPath.length,
    router.asPath.indexOf('#') > 0 ? router.asPath.indexOf('#') : router.asPath.length
  ])
  const pathname = router.asPath.substring(1, pathEnd)

  const components = [hostUrl]

  // 非預設 locale 需要加 locale
  if(router.locale !== router.defaultLocale) {
    components.push(router.locale)
  }

  if(pathname.length > 0) {
    components.push(pathname)
  }

  return components.join('/')
}
