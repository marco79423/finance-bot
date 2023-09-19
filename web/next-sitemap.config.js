const {HostUrl} = require('./config/vars.config')


/** @type {import('next-sitemap').IConfig} */
module.exports = {
  siteUrl: HostUrl,
  generateRobotsTxt: true,
  exclude: ['*'], // 全部改用自動生成
  robotsTxtOptions: {
    additionalSitemaps: [
      `${HostUrl}/server-sitemap.xml`,
    ],
  },
}
