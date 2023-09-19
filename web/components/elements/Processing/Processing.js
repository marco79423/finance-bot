import React from 'react'
import Image from 'next/image'
import {useTranslation} from 'next-i18next'
import {css} from '@emotion/react'

import loadingImage from './images/processing.svg'


export default function Processing({...props}) {
  const styles = {
    root: css`
      // https://codepen.io/sosuke/pen/Pjoqqp
      filter: invert(27%) sepia(24%) saturate(2998%) hue-rotate(207deg) brightness(98%) contrast(98%)
    `
  }

  const {t} = useTranslation('base')

  return (
    <Image
      css={styles.root}
      height={36} width={36}
      alt={t('Processing')}
      src={loadingImage}

      {...props}
    />
  )
}

