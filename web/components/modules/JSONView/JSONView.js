import React from 'react'
import ReactJson from '@textea/json-viewer'
import {useTranslation} from 'next-i18next'

import {useNotifications} from '../../../hooks/notifications'

/**
 * 展示 JSON 的組件
 * @param {object} data -  JSON 內容
 * @param {number} indentWidth -  indent width
 * @returns {JSX.Element}
 */
export default function JSONView({data, indentWidth=2}) {
  const {t} = useTranslation('base')
  const notifications = useNotifications('base')

  const copyToClipboard = ({src}) => {
    const text = JSON.stringify(src)

    navigator.clipboard.writeText(text)
      .then(() => notifications.showSuccessMessage(t('Copied Successfully')))
  }

  return (
    <React.Suspense fallback={<div>{t('Loading')} ...</div>}>
      <ReactJson
        src={data}
        indentWidth={indentWidth}
        displayDataTypes={false}
        displayArrayKey={false}
        enableClipboard={copyToClipboard}
      />
    </React.Suspense>
  )
}
