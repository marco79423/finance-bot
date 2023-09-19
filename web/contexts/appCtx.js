import React from 'react'

const AppCtxContext = React.createContext(false)

export function AppCtxProvider({ctx, children}) {
  return (
    <AppCtxContext.Provider value={ctx}>
      {children}
    </AppCtxContext.Provider>
  )
}


export function useAppCtx() {
  return React.useContext(AppCtxContext)
}
