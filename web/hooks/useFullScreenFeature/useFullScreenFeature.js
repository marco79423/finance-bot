import React from 'react'
import {FullScreen, useFullScreenHandle} from 'react-full-screen'
import {isMobile} from 'react-device-detect'
import {css, useTheme} from '@emotion/react'

import FullScreenButton from './FullScreenButton'

export default function useFullScreenFeature() {
  const theme = useTheme()
  const styles = {
    root: css`
      height: 100%;
      background: ${theme.palette.surface.light};
    `,
  }

  const inputFullScreenHandle = useFullScreenHandle()

  const Button = React.useCallback(() => {
    return (
      <FullScreenButton disabled={isMobile} onClick={inputFullScreenHandle.enter}/>
    )
  }, [])

  const Container = React.useCallback(({children, ...props}) => {
    return (
      <FullScreen css={styles.root} handle={inputFullScreenHandle} {...props}>
        {children}
      </FullScreen>
    )
  }, [])

  return [Button, Container]
}
