module.exports = {
  i18n: {
    defaultLocale: 'zh-TW',
    locales: ['zh-TW'],
  },

  defaultNS: 'base',

  // 自動 reload 更新翻譯
  reloadOnPrerender: process.env.NODE_ENV === 'development',
}
