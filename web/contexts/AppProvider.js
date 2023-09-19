import React from 'react'
import {ProviderCompose} from '@paji-sdk/web'
import {QueryClient, QueryClientProvider} from 'react-query'
import {SessionProvider} from 'next-auth/react'

import {NotificationsProvider} from '../hooks/notifications'
import {ThemeProvider} from '../hooks/theme'
import {DarkModeProvider} from '../hooks/darkMode'
import {DeveloperModeProvider} from './developerMode'
import {AppCtxProvider} from './appCtx'
import {ToolInfoProvider} from './toolInfo'

const queryClient = new QueryClient()

/**
 * 所有 App 所需的 Provider
 * @param children
 * @returns {JSX.Element}
 * @constructor
 */
function AppProvider({pageProps, children}) {
  return (
    <ProviderCompose.Composer providers={[
      ProviderCompose.provider(SessionProvider, {session: pageProps.session}),

      // React Query 的 Provider
      ProviderCompose.provider(QueryClientProvider, {client: queryClient}),

      // Context
      ProviderCompose.provider(AppCtxProvider, {ctx: pageProps.ctx}),
      ProviderCompose.provider(ToolInfoProvider, {ctx: pageProps.ctx}),
      ProviderCompose.provider(DeveloperModeProvider, {ctx: pageProps.ctx}),
      ProviderCompose.provider(DarkModeProvider),
      ProviderCompose.provider(ThemeProvider),
      ProviderCompose.provider(NotificationsProvider),
    ]}>
      {children}
    </ProviderCompose.Composer>
  )
}

export default AppProvider
