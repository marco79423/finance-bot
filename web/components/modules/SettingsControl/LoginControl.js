import {useSession, signIn, signOut} from 'next-auth/react'

export default function LoginControl() {
  const {data: session, status} = useSession()
  console.log('[login]', session, status)

  if (session) {
    return (
      <>
        Signed in as {session.user.email} <br/>
        <button onClick={() => signOut()}>Sign out</button>
      </>
    )
  }
  return (
    <>
      Not signed in <br/>
      <button onClick={() => signIn()}>Sign in</button>
    </>
  )
}