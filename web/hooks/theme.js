import React from 'react'
import {ThemeProvider as EmotionThemeProvider} from '@emotion/react'

import {useDarkMode} from './darkMode'
import darkTheme from '../themes/darkTheme'
import lightTheme from '../themes/defaultTheme'

export function ThemeProvider({children}) {
  const [darkMode] = useDarkMode()
  return (
    <EmotionThemeProvider theme={darkMode ? darkTheme : lightTheme}>
      {children}
    </EmotionThemeProvider>
  )
}
