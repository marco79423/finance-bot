import React from 'react'

const DefaultOptions = {
  enabled: true
}

export default function useInterval(callback, interval=1000, options) {
  const {enabled} = {...DefaultOptions, ...options}

  const ref = React.useRef(callback)
  React.useEffect(() => {
    ref.current = callback
  }, [callback])

  React.useEffect(() => {
    let intervalId
    if (enabled) {
      intervalId = setInterval(() => {
        ref.current()
      }, interval)
    }

    return () => {
      if(intervalId){
        clearInterval(intervalId)
      }
    }
  }, [interval, enabled])
}
