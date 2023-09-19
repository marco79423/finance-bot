import React from 'react'

const ToolInfoContext = React.createContext(false)

export function ToolInfoProvider({ctx, children}) {
  return (
    <ToolInfoContext.Provider value={ctx?.toolInfo}>
      {children}
    </ToolInfoContext.Provider>
  )
}


export function useToolInfo() {
  return React.useContext(ToolInfoContext)
}
