import React from 'react'
import {setCookie} from 'cookies-next'

import useKeyPressToggle from '../hooks/useKeyPressToggle'

export const DeveloperModeKey = 'DEVELOPER_MODE'

const DeveloperModeContext = React.createContext(false)

export function DeveloperModeProvider({ctx, children}) {
  const developMode = useKeyPressToggle(!!ctx?.developMode, 'F9')
  React.useEffect(() => {
    setCookie(DeveloperModeKey, developMode ? '1': '0')
  }, [developMode])

  return (
    <DeveloperModeContext.Provider value={developMode}>
      {children}
    </DeveloperModeContext.Provider>
  )
}


export function useDeveloperMode() {
  return React.useContext(DeveloperModeContext)
}
