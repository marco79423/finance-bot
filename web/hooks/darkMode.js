import React from 'react'
import {getCookie, setCookie} from 'cookies-next'

const DarkModeContext = React.createContext({})

export function DarkModeProvider({children}) {
  const [darkMode, setDarkMode] = React.useState(false)
  React.useEffect(() => {
    setDarkMode(!!+getCookie('DARK_MODE'))
  }, [])

  const setDarkModeWrapped = React.useCallback((value) => {
    setCookie('DARK_MODE', value ? '1' : '0')
    setDarkMode(value)
  }, [])

  const value = React.useMemo(() => {
    return {
      darkMode,
      setDarkMode: setDarkModeWrapped
    }
  }, [darkMode, setDarkModeWrapped])

  return (
    <DarkModeContext.Provider value={value}>
      {children}
    </DarkModeContext.Provider>
  )
}


export function useDarkMode() {
  const {darkMode, setDarkMode} = React.useContext(DarkModeContext)
  return [darkMode, setDarkMode]
}
