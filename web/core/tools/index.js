import lodash from 'lodash'

import TWStockAnalysis from './TWStockAnalysis'



export const AllToolConfigs = [
  {
    key: 'tw-stock-analysis',
    category: 'tw-stock',
    group: 'analysis',
    url: '/tw-stock-analysis',
    isPrivate: false,
    Component: TWStockAnalysis,
  },
]

export const AllToolConfigMap = AllToolConfigs
  .reduce((toolConfigMap, tool) => ({
    ...toolConfigMap,
    [tool.key]: tool,
  }), {})


export const AllToolInfos = AllToolConfigs.map(tool => lodash.omit(tool, 'Component'))

export const AllToolInfoMap = AllToolInfos
  .reduce((toolInfoMap, tool) => ({
    ...toolInfoMap,
    [tool.key]: tool,
  }), {})

