import React from 'react'
import {useRouter} from 'next/router'

export default function useInputQuery(defaultInput = '') {
  const router = useRouter()

  const [input, setInput] = React.useState(defaultInput)
  React.useEffect(() => {
    if (!router || !router.isReady) {
      return
    }

    if (input) {
      router.replace({
        query: {...router.query, input}
      })
    } else {
      delete router.query['input']
      router.replace({
        query: router.query
      })
    }
  }, [input])

  React.useEffect(() => {
    if (!router || !router.isReady) {
      return
    }

    if (router.query.input) {
      setInput(router.query.input)
    }
  }, [router])

  return [input, setInput]
}
