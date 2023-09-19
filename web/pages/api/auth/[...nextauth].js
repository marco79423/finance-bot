import NextAuth from 'next-auth'
import GoogleProvider from 'next-auth/providers/google'

export const authOptions = {
  // Configure one or more authentication providers
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    }),
  ],
  callbacks: {
    async signIn({user, account, profile, email, credentials}) {
      console.log(['[signIn]', user, account, profile, email, credentials])
      return true
    },

    async redirect({ url, baseUrl }) {
      console.log('[redirect]', url, baseUrl)
      return baseUrl
    },

    async jwt({token, account}) {
      // Persist the OAuth access_token to the token right after signin
      console.log('[jwt] Persist the OAuth access_token to the token right after signin')
      console.log('[jwt] account', account)
      console.log('[jwt] token', token)

      if (account) {
        token.accessToken = account.access_token
      }
      return token
    },
    async session({session, token, user}) {
      // Send properties to the client, like an access_token from a provider.
      console.log('[session] session', session)
      console.log('[session] token', token)
      console.log('[session] user', user)
      session.accessToken = token.accessToken
      return session
    }
  }
}


export default NextAuth(authOptions)