import React from 'react'
import {useTranslation} from 'next-i18next'
import {css} from '@emotion/react'
import Processing from '../elements/Processing'


function ImageArea({source, loading, ...props}) {
  const styles = {
    root: css`
      position: relative;
      width: 100%;
      height: 100%;
      
      display: flex;
      align-items: center;
      justify-content: center;
    `,

    image: css`
      max-width: 100%;
      max-height: 100%;

      height: fit-content;
      width: fit-content;
    `,

    loadingCover: css`
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      
      background: rgba(63, 81, 181, 0.1);
    `
  }

  const {t} = useTranslation('base')

  if (!source) {
    return null
  }

  if (source instanceof Error) {
    return (
      <span>{source.toString()}</span>
    )
  }

  return (
    <div css={styles.root} {...props}>
      <object css={styles.image} data={loading ? '' : source}>
        <span>{t('Preview is not supported.')}</span>
      </object>
      {loading && (
        <div css={styles.loadingCover}>
          <Processing/>
        </div>
      )}
    </div>
  )
}

export default React.memo(ImageArea)