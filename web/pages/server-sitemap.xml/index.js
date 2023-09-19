import fp from 'lodash/fp'
import {getServerSideSitemap} from 'next-sitemap'

import i18config from '../../next-i18next.config'
import {HostUrl} from '../../config/vars.config'
import {AllToolInfos} from '../../core/tools'

export const getServerSideProps = async (ctx) => {
  const lastmod = new Date().toISOString()
  const changefreq = 'daily'
  const priority = 0.7

  const sitemaps = fp.flow(
    fp.filter(toolInfo => !toolInfo.isPrivate),
    fp.filter(toolInfo => !toolInfo.url.startsWith('http')),
    fp.map(toolInfo => i18config.i18n.locales.map(locale => ({
      loc: locale === 'en' ? `${HostUrl}${toolInfo.url}` : `${HostUrl}/${locale}${toolInfo.url}`,
      lastmod,
      changefreq,
      priority,
      alternateRefs: i18config.i18n.locales.map(locale => ({
        href: locale === 'en' ? `${HostUrl}${toolInfo.url}` : `${HostUrl}/${locale}${toolInfo.url}`,
        hreflang: locale,
      })),
    }))),
    fp.flatten,
  )(AllToolInfos)

  return getServerSideSitemap(ctx, sitemaps)
}


export default function Sitemap() {

}